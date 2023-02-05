from abc import ABC, abstractmethod
from typing import Any
from datetime import datetime
import asyncio

from .CommandsManager import CommandsManager
from .Command import Command
from .Response import Response, ResponseAction
from .ThreadData import ThreadData


class CommandContext:
    commands: list[Command] = []
    parameters: dict[str, Any]

    def __init__(self, commands, parameters = {}):
        self.commands = commands
        self.parameters = parameters

class CommandsContextManagerDelegate(ABC):
    @abstractmethod
    def commandsContextDidReceiveResponse(self, response: Response): 
        pass

class CommandsContextManager:

    delegate: CommandsContextManagerDelegate

    commandsManager = CommandsManager()
    lastInteractTime: datetime = datetime.now()

    contextQueue: list[CommandContext] = []
    threads: list[ThreadData] = []
    reports: list[Response] = []
    memory: list[Response] = []

    delaysReports: False # if True, reports will be delayed to next interaction; if False send reports immediately

    def __init__(self, delegate: CommandsContextManagerDelegate):
        self.delegate = delegate

    @property
    def rootContext(self):
        return CommandContext(self.commandsManager.commands)

    def processString(self, string: str, data: dict[str, Any] = {}):
        if not self.contextQueue:
            self.contextQueue.append(self.rootContext)

        currentContext = self.contextQueue[0]

        while self.contextQueue:
            
            searchResults = self.commandsManager.search(string = string, commands = currentContext.commands)
            
            if not searchResults:
                currentContext = self.contextQueue.pop(0)
                continue

            for searchResult in searchResults:

                parameters = {**currentContext.parameters, **searchResult.parameters}
                commandResponse = searchResult.command.start(parameters)
                # commandResponse.data = data

                # needContinue = False

                for action in commandResponse.actions:
                    match action:
                        case ResponseAction.popContext:
                            self.contextQueue.pop(0)
                        case ResponseAction.popToRootContext:
                            self.contextQueue = [self.commandsManager.allCommands,]
                        case ResponseAction.sleep:
                            self.speechRecognizer.isRecognizing = False
                        case ResponseAction.repeatLastAnswer:
                            if self.memory:
                                previousResponse = self.memory[-1]
                                self.delegate.didReceiveCommandsResponse(previousResponse)
                        case ResponseAction.commandNotFound:
                            # needContinue = not self.commandsManager.stringHasName(string)
                            pass

                # if needContinue: 
                #     continue
                
                self.parse(commandResponse)
                # break

    async def asyncCheckThreads(self):
        while True:
            await asyncio.sleep(5)
            self.checkThreads()

    def checkThreads(self):
        for threadData in self.threads:
            if not threadData.finishEvent.is_set(): continue

            response = threadData.thread.join()
            self.parse(response, delaysReports = self.delaysReports and datetime.now().timestamp() - self.lastInteractTime.timestamp() > 30)
            threadData.finishEvent.clear()

            del threadData

    def parse(self, response, delaysReports: bool = False):
        self.reports.insert(0, response)
        
        if response.thread:
            self.threads.append(response.thread)
        
        if response.context:
            newContext = CommandContext(response.context, response.parameters)
            self.contextQueue.insert(0, newContext)
        
        if not delaysReports:
            self.report()
        
        self.memory.append(response)

    def report(self):
        while self.reports:
            rep = self.reports.pop(0)
            self.delegate.commandsContextDidReceiveResponse(rep)
