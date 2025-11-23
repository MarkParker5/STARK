from __future__ import annotations

import logging
import warnings
from types import AsyncGeneratorType, GeneratorType
from typing import Any, Protocol, runtime_checkable

import anyio
from asyncer import syncify
from asyncer._main import TaskGroup

from stark.core.commands_context_processor import (
    CommandsContextLayer,
    RecognizedEntity,
)
from stark.core.parsing import PatternParser
from stark.core.types.object import Object

from ..general.dependencies import DependencyManager, default_dependency_manager
from .command import (
    AsyncResponseHandler,
    Command,
    CommandRunner,
    Response,
    ResponseHandler,
    ResponseOptions,
)
from .commands_manager import CommandsManager

logger = logging.getLogger(__name__)


@runtime_checkable
class CommandsContextDelegate(Protocol):
    async def commands_context_did_receive_response(self, response: Response):
        pass

    def remove_response(self, response: Response):
        pass


class CommandsContext:
    is_stopped = False
    commands_manager: CommandsManager
    dependency_manager: DependencyManager
    pattern_parser: PatternParser
    last_response: Response | None = None
    context_queue: list[CommandsContextLayer]

    _delegate: CommandsContextDelegate | None = None
    _response_queue: list[Response]
    _task_group: TaskGroup

    def __init__(
        self,
        task_group: TaskGroup,
        commands_manager: CommandsManager,
        dependency_manager: DependencyManager = default_dependency_manager,
        processors: list[Any] | None = None,
    ):
        assert isinstance(task_group, TaskGroup), task_group
        assert isinstance(commands_manager, CommandsManager)
        assert isinstance(dependency_manager, DependencyManager)
        self.pattern_parser = PatternParser()
        self.commands_manager = commands_manager
        self.context_queue = [self.root_context]
        self._response_queue = []
        self._task_group = task_group
        self.dependency_manager = dependency_manager
        self.dependency_manager.add_dependency(None, AsyncResponseHandler, self)
        self.dependency_manager.add_dependency(None, ResponseHandler, SyncResponseHandler(self))
        self.dependency_manager.add_dependency("inject_dependencies", None, self.inject_dependencies)
        from .commands_context_search_processor import CommandsContextSearchProcessor

        self.processors = processors if processors is not None else [CommandsContextSearchProcessor()]

    @property
    def delegate(self) -> CommandsContextDelegate:
        assert self._delegate is not None
        return self._delegate

    @delegate.setter
    def delegate(self, delegate: CommandsContextDelegate | None):
        assert isinstance(delegate, CommandsContextDelegate) or delegate is None
        self._delegate = delegate

    @property
    def root_context(self):
        return CommandsContextLayer(self.commands_manager.commands, {})

    async def process_string(self, string: str):
        if not self.context_queue:
            self.context_queue.append(self.root_context)

        # Run the string and context queue through all the processors

        recognized_entities: list[RecognizedEntity] = []
        search_results: list[Any] = []
        context_pops: int = 0

        for processor in self.processors:
            logger.debug(f"Processing context {processor=} with {string=} {recognized_entities=} {self.context_queue=}")
            search_results, context_pops = await processor.process_string(string, self, recognized_entities)
            if search_results:
                # Pop contexts as directed by processor
                for _ in range(context_pops):
                    if self.context_queue:
                        self.context_queue.pop(0)
                break
        else:  # no results found at all
            self.context_queue = [self.root_context]  # nothing found, reset to root context

        # Prepare and execute found commands;

        for search_result in search_results or []:
            current_context = self.context_queue[0]
            parameters: dict[str, Object] = {}
            parameters.update(current_context.parameters)
            parameters.update(search_result.match_result.parameters)
            parameters.update(self.dependency_manager.resolve(search_result.command._runner))
            self.run_command(search_result.command, parameters)

        return search_results or []

    def inject_dependencies(self, runner: Command[CommandRunner] | CommandRunner) -> CommandRunner:
        def injected_func(**kwargs) -> ResponseOptions:
            kwargs.update(self.dependency_manager.resolve(runner._runner if isinstance(runner, Command) else runner))
            return runner(**kwargs)  # type: ignore

        return injected_func  # type: ignore

    def run_command(self, command: Command, parameters: dict[str, Any] = {}):
        async def command_task():
            command_return = await command(parameters)

            if isinstance(command_return, Response):
                await self.respond(command_return)

            elif isinstance(command_return, AsyncGeneratorType):
                async for response in command_return:
                    if response:
                        await self.respond(response)

            elif isinstance(command_return, GeneratorType):
                message = (
                    f"[WARNING] Command {command} is a sync GeneratorType that is not fully supported and may block the main thread. "
                    + "Consider using the ResponseHandler.respond() or async approach instead."
                )
                warnings.warn(message, UserWarning)
                for response in command_return:
                    if response:
                        await self.respond(response)

            elif command_return is None:
                pass

            else:
                raise TypeError(
                    f"Command {command} returned {command_return} of type {type(command_return)} instead of Response or AsyncGeneratorType[Response]"
                )

        self._task_group.soonify(command_task)()

    # ResponseHandler

    async def respond(self, response: Response):  # async forces to run in main thread
        assert isinstance(response, Response)
        self._response_queue.append(response)

    async def unrespond(self, response: Response):
        if response in self._response_queue:
            self._response_queue.remove(response)
        self.delegate.remove_response(response)

    async def pop_context(self):
        self.context_queue.pop(0)

    # Context

    def pop_to_root_context(self):
        self.context_queue = [self.root_context]

    def add_context(self, context: CommandsContextLayer):
        self.context_queue.insert(0, context)

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
            self.context_queue.insert(0, newContext)

        await self.delegate.commands_context_did_receive_response(response)


class SyncResponseHandler:  # needs for changing thread from worker to main in commands ran with asyncify
    async_response_handler: ResponseHandler

    def __init__(self, async_response_handler: ResponseHandler):
        self.async_response_handler = async_response_handler

    # ResponseHandler
    # TODO: review

    def respond(self, response: Response):
        syncify(self.async_response_handler.respond)(response)

    def unrespond(self, response: Response):
        syncify(self.async_response_handler.unrespond)(response)

    def pop_context(self):
        syncify(self.async_response_handler.pop_context)()
