#!/usr/local/bin/python3.8
from typing import Optional
import asyncio
import os

import config
from ..Control import Control
from General import SpeechRecognizer, Text2Speech
from ArchieCore import CommandsManager, Command, Response, ResponseAction, ThreadData, ACTime

class VoiceAssistant(Control):
    commandsManager = CommandsManager()
    speechRecognizer = SpeechRecognizer()
    voice = Text2Speech.Engine()

    commandsContext: list[list[Command]] = []
    threads: list[ThreadData] = []
    reports: list[Response] = []
    memory: list[Response] = []

    voids: int = 0
    lastInteractTime: ACTime = ACTime()
    lastClapTime: float = 0
    doubleClap: bool = False

    def __init__(self):
        pass

    def start(self):
        self.commandsContext = [self.commandsManager.allCommands,]
        self.speechRecognizer.didReceivePartialResult = lambda string: self.speechRecognizerReceivePartialResult(string)
        self.speechRecognizer.didReceiveFinalResult = lambda string: self.speechRecognizerReceiveFinalResult(string)
        self.speechRecognizer.didReceiveEmptyResult = lambda: self.speechRecognizerReceiveEmptyResult()

        asyncio.get_event_loop().run_until_complete(
            self.listenAndCheckThreads()
        )

    def stop(self):
        self.speechRecognizer.stopListening()

    def speechRecognizerReceiveEmptyResult(self):
        self.voids += 1

    def speechRecognizerReceivePartialResult(self, result: str):
        print(f'\rYou: \x1B[3m{result}\x1B[0m', end = '')

    def speechRecognizerReceiveFinalResult(self, result: str):
        self.voids = 0
        self.lastInteractTime = ACTime()
        print(f'\rYou: {result}')

        currentContext = self.commandsContext[0] if self.commandsContext else None

        while self.commandsContext:
            if searchResults := self.commandsManager.search(string = result, commands = currentContext):
                for searchResult in searchResults:
                    commandResponse = searchResult.command.start(params = searchResult.parameters)
                    self.parse(commandResponse)

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
                                self.reply(previousResponse)
                break
            else:
                currentContext = self.commandsContext.pop(0)
        else:
            self.commandsContext.append(self.commandsManager.allCommands)

    async def listenAndCheckThreads(self):
        while True:
            await self.speechRecognizer.startListening()

            for threadData in self.threads:
                if not threadData.finishEvent.is_set(): continue

                response = threadData.thread.join()
                self.parse(response, silent = ACTime() - self.lastInteractTime > 30)
                threadData.finishEvent.clear()

                del threadData

    def parse(self, response, silent: bool = False):
        self.reports.insert(0, response)
        if not silent:
            self.report()
        if response.thread:
            self.threads.append(response.thread)
        if response.context:
            self.commandsContext.insert(0, response.context)
        self.memory.append(response)

    def report(self):
        for response in self.reports:
            self.reply(response)
        self.reports = []

    def reply(self, response):
        if response.text:
            print(f'\nArchie: {response.text}')
        if response.voice:
            wasRecognizing = self.speechRecognizer.isRecognizing
            self.speechRecognizer.isRecognizing = False
            self.voice.generate(response.voice).speak()
            self.speechRecognizer.isRecognizing = wasRecognizing

    # check double clap from arduino microphone module
    def checkClap(self, channel):
        now = time.time()
        delta = now - self.lastClapTime
        if 0.1 < delta < 0.6:
            self.speechRecognizer.isRecognizing = True
        else:
            self.lastClapTime = now

if config.double_clap_activation:
    import RPi.GPIO as GPIO

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(12, GPIO.IN)
    GPIO.add_event_detect(12, GPIO.RISING, callback = VoiceAssistant().checkClap)
