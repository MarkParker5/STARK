from typing import Any, Protocol
from dataclasses import dataclass
import asyncio

from .CommandsManager import CommandsManager
from .Command import Command, Response, ResponseHandler
from .Threads import ThreadData


@dataclass
class CommandsContextLayer:
    commands: list[Command]
    parameters: dict[str, Any]

class CommandsContextDelegate(Protocol):
    def commands_context_did_receive_response(self, response: Response): pass

class CommandsContext:

    delegate: CommandsContextDelegate
    commands_manager: CommandsManager

    last_response: Response = None
    _context_queue: list[CommandsContextLayer]
    _threads: list[ThreadData]
    
    def __init__(self, commands_manager):
        self.commands_manager = commands_manager
        self._context_queue = [self.root_context]
        self._threads = []

    @property
    def root_context(self):
        return CommandsContextLayer(self.commands_manager.commands, {})

    def process_string(self, string: str):
        
        if not self._context_queue:
            self._context_queue.append(self.root_context)

        # search commands
        while self._context_queue:
            
            current_context = self._context_queue[0]
            search_results = self.commands_manager.search(string = string, commands = current_context.commands)
            
            if search_results:
                break
            else:
                self._context_queue.pop(0)

        for search_result in search_results:

            parameters = {**current_context.parameters, **search_result.match_result.parameters}
            
            # pass dependencies as parameters
            for name, annotation in search_result.command._runner.__annotations__.items():
                if annotation == ResponseHandler:
                    parameters[name] = self
            
            # execute command
            command_response = search_result.command(parameters)
            
            if not command_response:
                continue
            
            # process response
            if command_response is Response.repeat_last and self.last_response:
                self.process_response(self.last_response)
            else:
                self.process_response(command_response)

    # ResponseHandler
    
    def process_response(self, response: Response):
        self.last_response = response 
        
        if response.thread:
            self._threads.append(response.thread)
        
        if response.commands:
            newContext = CommandsContextLayer(response.commands, response.parameters)
            self._context_queue.insert(0, newContext)
        
        self.delegate.commands_context_did_receive_response(response)
         
    def remove_response(self, response: Response): 
        self.delegate.remove_response(response)
    
    def pop_context(self):
        self._context_queue.pop(0)
    
    # Context
    
    def pop_to_root_context(self):
        self._context_queue = [self.root_context]
    
    def add_context(self, context: CommandsContextLayer):
        self._context_queue.insert(0, context)

    # Threads

    async def async_check_threads(self):
        while True:
            await asyncio.sleep(5)
            self._check_threads()

    def _check_threads(self):
        for thread_data in self._threads:
            if not thread_data.finish_event.is_set(): continue

            response = thread_data.thread.join()
            self.process_response(response)
            thread_data.finish_event.clear()

            del thread_data