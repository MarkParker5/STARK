#!/usr/local/bin/python3.8
from typing import Optional

import os

import config
from ..Control import Control
from General import SpeechRecognizer, Text2Speech
from ArchieCore import CommandsManager, Command, Response, ResponseAction, ThreadData

'''
TODO: async
self.check_threads()
self.report()
'''

class VoiceAssistant(Control):
    commandsManager = CommandsManager()
    speechRecognizer = SpeechRecognizer()
    voice = Text2Speech.Engine()

    commandsContext: list[list[Command]] = []
    threads: list[ThreadData] = []
    reports: list[Response] = []
    memory: list[Response] = []

    voids: int = 0
    lastClapTime: float = 0
    doubleClap: bool = False

    def __init__(self):
        pass

    def start(self):
        self.commandsContext = [self.commandsManager.allCommands,]
        self.speechRecognizer.didReceivePartialResult = lambda string: self.speechRecognizerReceivePartialResult(string)
        self.speechRecognizer.didReceiveFinalResult = lambda string: self.speechRecognizerReceiveFinalResult(string)
        self.speechRecognizer.startListening()

    def stop(self):
        self.speechRecognizer.stopListening()

    def speechRecognizerReceivePartialResult(self, result: str):
        print(f'\rYou: \x1B[3m{result}\x1B[0m', end = '')

    def speechRecognizerReceiveFinalResult(self, result: str):
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
                            break
                        case ResponseAction.sleep:
                            self.stopListening()
                        case ResponseAction.repeatLastAnswer:
                            if self.memory:
                                previousResponse = self.memory[-1]
                                self.reply(previousResponse)
                break
            else:
                currentContext = self.commandsContext.pop(0)
        else:
            self.commandsContext.append(self.commandsManager.allCommands)

    def parse(self, response):
        self.reply(response)
        if response.thread:                               #   add background thread to list
            self.threads.append(response.thread)
        if response.context:                              #   insert context if exist
            self.commandsContext.insert(0, response.context)
        self.memory.append(response)

    def reply(self, response):
        if response.text:                                 #   print answer
            print('\nArchie: '+response.text)
        if response.voice:                                #   say answer
            self.voice.generate(response.voice).speak()

    def report(self):
        for response in self.reports:
            self.reply(response)
        self.reports = []

    def check_threads(self):
        for thread in self.threads:
            if not thread['finish_event'].is_set(): continue
            response = thread['thread'].join()
            self.reply(response)
            if response.callback:
                if response.callback.quiet:
                    response.callback.start()
                else:
                    for _ in range(3):
                        print('\nYou: ', end='')
                        speech = self.listener.listen()
                        if speech['status'] == 'ok':
                            print(speech['text'], '\n')
                            new_response = response.callback.answer(speech['text'])
                            self.reply(new_response)
                            break
                    else:
                        self.reports.append(response)
            thread['finish_event'].clear()
            del thread

    # check double clap from arduino microphone module
    def checkClap(self, channel):
        now = time.time()
        delta = now - self.lastClapTime
        if 0.1 < delta < 0.6:
            self.doubleClap = True
        else:
            self.lastClapTime = now

    # waiting for double clap
    def sleep(self):
        self.lastClapTime = 0
        while not self.doubleClap:
            self.check_threads()
            time.sleep(1)
        else:
            self.doubleClap = False

if config.double_clap_activation:
    import RPi.GPIO as GPIO
    import time

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(12, GPIO.IN)
    GPIO.add_event_detect(12, GPIO.RISING, callback = VoiceAssistant().checkClap)

if __name__ == '__main__':
    VoiceAssistant().start()
