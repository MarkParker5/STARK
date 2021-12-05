from abc import ABC, abstractmethod
import asyncio
from typing import Any

from ArchieCore import ACTime
from .CommandsManager import CommandsManager
from .Command import Command
from .Response import Response, ResponseAction
from .ThreadData import ThreadData

class CommandsContextDelegate:
    @abstractmethod
    def commandsContextDidReceiveResponse(self, response: Response): pass

class CommandsContext:

    delegate: CommandsContextDelegate

    commandsManager = CommandsManager()
    lastInteractTime: ACTime = ACTime()
    commandsContext: list[list[Command]] = [CommandsManager().allCommands,]
    threads: list[ThreadData] = []
    reports: list[Response] = []
    memory: list[Response] = []
    delaysReports: False # if True, reports will be delayed to next interaction; if False send reports immediately

    def __init__(self, delegate: CommandsContextDelegate):
        self.delegate = delegate

    def processString(self, string: str, data: dict[str, Any] = {}):
        currentContext = self.commandsContext[0] if self.commandsContext else None

        while self.commandsContext:
            if searchResults := self.commandsManager.search(string = string, commands = currentContext):
                for searchResult in searchResults:
                    commandResponse = searchResult.command.start(params = searchResult.parameters)
                    commandResponse.data = data

                    match commandResponse.action:
                        case ResponseAction.popContext:
                            self.commandsContext.pop(0)
                        case ResponseAction.popToRootContext:
                            self.commandsContext = [self.commandsManager.allCommands,]
                        case ResponseAction.sleep:
                            self.speechRecognizer.isRecognizing = False
                        case ResponseAction.repeatLastAnswer:
                            if self.memory:
                                previousResponse = self.memory[-1]
                                self.delegate.didReceiveCommandsResponse(previousResponse)
                        case ResponseAction.answerNotFound:
                            continue

                    self.parse(commandResponse)
                break
            else:
                currentContext = self.commandsContext.pop(0)
        else:
            self.commandsContext.append(self.commandsManager.allCommands)

    async def asyncCheckThreads(self):
        while True:
            await asyncio.sleep(5)
            checkThreads()

    def checkThreads(self):
        for threadData in self.threads:
            if not threadData.finishEvent.is_set(): continue

            response = threadData.thread.join()
            self.parse(response, delaysReports = delaysReports and ACTime() - self.lastInteractTime > 30)
            threadData.finishEvent.clear()

            del threadData

    def parse(self, response, delaysReports: bool = False):
        self.reports.insert(0, response)
        if response.thread:
            self.threads.append(response.thread)
        if response.context:
            self.commandsContext.insert(0, response.context)
        if not delaysReports:
            self.report()
        self.memory.append(response)

    def report(self):
        for response in self.reports:
            self.delegate.commandsContextDidReceiveResponse(response)
        self.reports = []
