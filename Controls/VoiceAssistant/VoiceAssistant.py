#!/usr/local/bin/python3.8
from typing import Optional
import asyncio

import config
from ..Control import Control
from General import SpeechRecognizer, SpeechRecognizerDelegate, Text2Speech
from ArchieCore import ACTime, CommandsContextManager, CommandsContextManagerDelegate

class VoiceAssistant(Control, SpeechRecognizerDelegate, CommandsContextManagerDelegate):

    speechRecognizer: SpeechRecognizer
    CommandsContextManager: CommandsContextManager
    voice = Text2Speech.Engine()

    voids: int = 0
    lastClapTime: float = 0
    doubleClap: bool = False

    # Control

    def __init__(self):
        self.speechRecognizer = SpeechRecognizer(delegate = self)
        self.commandsContext = CommandsContextManager(delegate = self)

    def start(self):
        self.speechRecognizer.delegate = self
        print('Listen...')
        asyncio.get_event_loop().run_until_complete(
            self.speechRecognizer.startListening()
        )

    def stop(self):
        self.speechRecognizer.stopListening()

    # SpeechRecognizerDelegate

    def speechRecognizerReceiveFinalResult(self, result: str):
        self.voids = 0
        self.commandsContext.lastInteractTime = ACTime()
        print(f'\rYou: {result}')

        self.commandsContext.processString(result)

    def speechRecognizerReceivePartialResult(self, result: str):
        print(f'\rYou: \x1B[3m{result}\x1B[0m', end = '')

    def speechRecognizerReceiveEmptyResult(self):
        self.voids += 1

    # CommandsContextManagerDelegate

    def commandsContextDidReceiveResponse(self, response):
        if response.text:
            print(f'Archie: {response.text}')
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
