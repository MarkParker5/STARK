from abc import ABC, abstractmethod
from typing import Any
from datetime import datetime
import asyncio

from .CommandsManager import CommandsManager
from .Command import Command, Response, ResponseAction
from .Threads import ThreadData


class CommandsContextLayer:
    commands: list[Command] = []
    parameters: dict[str, Any]

    def __init__(self, commands, parameters = {}):
        self.commands = commands
        self.parameters = parameters

class CommandsContextDelegate(ABC):
    @abstractmethod
    def commands_context_did_receive_response(self, response: Response): 
        pass

class CommandsContext:

    delegate: CommandsContextDelegate

    commands_manager: CommandsManager

    context_queue: list[CommandsContextLayer]
    threads: list[ThreadData]
    reports: list[Response]
    memory: list[Response]

    delays_reports: bool = False # if True, reports will be delayed to next interaction; if False send reports immediately
    last_interact_time: datetime = datetime.now()

    def __init__(self, commands_manager):
        self.commands_manager = commands_manager
        self.context_queue = [self.root_context]
        self.threads = []
        self.reports = []
        self.memory = []

    @property
    def root_context(self):
        return CommandsContextLayer(self.commands_manager.commands)

    def process_string(self, string: str):
        if not self.context_queue:
            self.context_queue.append(self.root_context)

        while self.context_queue:
            
            current_context = self.context_queue[0]
            search_results = self.commands_manager.search(string = string, commands = current_context.commands)
            
            if search_results:
                break
            else:
                self.context_queue.pop(0)

        for search_result in search_results:

            parameters = {**current_context.parameters, **search_result.parameters}
            command_response = search_result.command.run(parameters)
            # command_response.data = data

            for action in command_response.actions:
                match action:
                    case ResponseAction.popContext:
                        self.context_queue.pop(0)
                    case ResponseAction.popToRootContext:
                        self.context_queue = [self.commands_manager.сommands,]
                    case ResponseAction.sleep:
                        self.speechRecognizer.is_recognizing = False
                    case ResponseAction.repeatLastAnswer:
                        if self.memory:
                            previousResponse = self.memory[-1]
                            self.delegate.didReceiveCommandsResponse(previousResponse)
                    case ResponseAction.commandNotFound:
                        pass
            
            self.parse(command_response)

    async def async_check_threads(self):
        while True:
            await asyncio.sleep(5)
            self.check_threads()

    def check_threads(self):
        for thread_data in self.threads:
            if not thread_data.finishEvent.is_set(): continue

            response = thread_data.thread.join()
            self.parse(response, delays_reports = self.delays_reports and datetime.now().timestamp() - self.last_interact_time.timestamp() > 30)
            thread_data.finishEvent.clear()

            del thread_data

    def parse(self, response, delays_reports: bool = False):
        self.reports.insert(0, response)
        
        if response.thread:
            self.threads.append(response.thread)
        
        if response.commands:
            newContext = CommandsContextLayer(response.commands, response.parameters)
            self.context_queue.insert(0, newContext)
        
        if not delays_reports:
            self.report()
        
        self.memory.append(response)

    def report(self):
        while self.reports:
            rep = self.reports.pop(0)
            self.delegate.commands_context_did_receive_response(rep)