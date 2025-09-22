from __future__ import annotations

import warnings
from dataclasses import dataclass
from types import AsyncGeneratorType, GeneratorType
from typing import Any, Protocol, runtime_checkable

import anyio
from asyncer import syncify
from asyncer._main import TaskGroup

from ..general.dependencies import DependencyManager, default_dependency_manager
from .command import (
    AsyncResponseHandler,
    Command,
    CommandRunner,
    Response,
    ResponseHandler,
    ResponseOptions,
)
from .commands_manager import CommandsManager, SearchResult


@dataclass
class CommandsContextLayer:
    commands: list[Command]
    parameters: dict[str, Any]

@runtime_checkable
class CommandsContextDelegate(Protocol):
    async def commands_context_did_receive_response(self, response: Response): pass
    def remove_response(self, response: Response): pass

class CommandsContext:

    is_stopped = False
    commands_manager: CommandsManager
    dependency_manager: DependencyManager
    last_response: Response | None = None
    fallback_command: Command | None = None

    _delegate: CommandsContextDelegate | None = None
    _response_queue: list[Response]
    _context_queue: list[CommandsContextLayer]
    _task_group: TaskGroup

    def __init__(self, task_group: TaskGroup, commands_manager: CommandsManager, dependency_manager: DependencyManager = default_dependency_manager):
        assert isinstance(task_group, TaskGroup), task_group
        assert isinstance(commands_manager, CommandsManager)
        assert isinstance(dependency_manager, DependencyManager)
        self.commands_manager = commands_manager
        self._context_queue = [self.root_context]
        self._response_queue = []
        self._task_group = task_group
        self.dependency_manager = dependency_manager
        self.dependency_manager.add_dependency(None, AsyncResponseHandler, self)
        self.dependency_manager.add_dependency(None, ResponseHandler, SyncResponseHandler(self))
        self.dependency_manager.add_dependency('inject_dependencies', None, self.inject_dependencies)

    @property
    def delegate(self):
        return self._delegate

    @delegate.setter
    def delegate(self, delegate: CommandsContextDelegate | None):
        assert isinstance(delegate, CommandsContextDelegate) or delegate is None
        self._delegate = delegate

    @property
    def root_context(self):
        return CommandsContextLayer(self.commands_manager.commands, {})

    async def process_string(self, string: str):

        if not self._context_queue:
            self._context_queue.append(self.root_context)

        # search commands
        search_results = []
        while self._context_queue:

            current_context = self._context_queue[0]
            search_results = await self.commands_manager.search(string = string, commands = current_context.commands)

            if search_results:
                break
            else:
                self._context_queue.pop(0)

        if not search_results and self.fallback_command and (matches := await self.fallback_command.pattern.match(string)):
            for match in matches:
                search_results = [SearchResult(
                    command = self.fallback_command,
                    match_result = match,
                    index = 0
                )]

        for search_result in search_results or []:

            parameters = current_context.parameters
            parameters.update(search_result.match_result.parameters)
            parameters.update(self.dependency_manager.resolve(search_result.command._runner))

            self.run_command(search_result.command, parameters)

    def inject_dependencies(self, runner: Command[CommandRunner] | CommandRunner) -> CommandRunner:
        def injected_func(**kwargs) -> ResponseOptions:
            kwargs.update(self.dependency_manager.resolve(runner._runner if isinstance(runner, Command) else runner))
            return runner(**kwargs) # type: ignore
        return injected_func # type: ignore

    def run_command(self, command: Command, parameters: dict[str, Any] = {}):
        async def command_runner():
            command_return = await command(parameters)

            if isinstance(command_return, Response):
                await self.respond(command_return)

            elif isinstance(command_return, AsyncGeneratorType):
                async for response in command_return:
                    if response:
                        await self.respond(response)

            elif isinstance(command_return, GeneratorType):
                message = f'[WARNING] Command {command} is a sync GeneratorType that is not fully supported and may block the main thread. ' + \
                            'Consider using the ResponseHandler.respond() or async approach instead.'
                warnings.warn(message, UserWarning)
                for response in command_return:
                    if response:
                        await self.respond(response)

            elif command_return is None:
                pass

            else:
                raise TypeError(f'Command {command} returned {command_return} of type {type(command_return)} instead of Response or AsyncGeneratorType[Response]')

        self._task_group.soonify(command_runner)()

    # ResponseHandler

    async def respond(self, response: Response): # async forces to run in main thread
        assert isinstance(response, Response)
        self._response_queue.append(response)

    async def unrespond(self, response: Response):
        if response in self._response_queue:
            self._response_queue.remove(response)
        self.delegate.remove_response(response)

    async def pop_context(self):
        self._context_queue.pop(0)

    # Context

    def pop_to_root_context(self):
        self._context_queue = [self.root_context]

    def add_context(self, context: CommandsContextLayer):
        self._context_queue.insert(0, context)

    # ResponseQueue

    async def handle_responses(self):
        self.is_stopped = False
        while not self.is_stopped:
            while self._response_queue:
                await self._process_response(self._response_queue.pop(0))
            await anyio.sleep(0.01)

    def stop(self):
        self.is_stopped = True

    async def _process_response(self, response: Response):
        if response is Response.repeat_last and self.last_response:
            await self._process_response(self.last_response)
            return

        if response is not Response.repeat_last:
            self.last_response = response

        if response.commands:
            newContext = CommandsContextLayer(response.commands, response.parameters)
            self._context_queue.insert(0, newContext)

        await self.delegate.commands_context_did_receive_response(response)

class SyncResponseHandler: # needs for changing thread from worker to main in commands ran with asyncify

    async_response_handler: ResponseHandler

    def __init__(self, async_response_handler: ResponseHandler):
        self.async_response_handler = async_response_handler

    # ResponseHandler

    def respond(self, response: Response):
        syncify(self.async_response_handler.respond)(response)

    def unrespond(self, response: Response):
        syncify(self.async_response_handler.unrespond)(response)

    def pop_context(self):
        syncify(self.async_response_handler.pop_context)()
