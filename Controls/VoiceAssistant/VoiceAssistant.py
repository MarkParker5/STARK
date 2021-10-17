#!/usr/local/bin/python3.8
import os
from Controls.Control import Control
from General import SpeechRecognition, Text2Speech
from Features.Command import Command
import config

class VoiceAssistant(Control):
    listener = SpeechRecognition.SpeechToText()
    voice    = Text2Speech.Engine()
    threads  = []
    reports  = []
    memory   = []
    voids    = 0

    lastClapTime = 0
    doubleClap = False

    def start(self):
        self.listener.listen_noise()
        os.system('clear')

        while True:
            if self.voids >= 3:
                self.voids = 0
                if config.double_clap_activation:
                    print('\nSleep (-_-)zzZZ\n')
                    sleep()
            print('\nYou: ', end='')
            speech = self.listener.listen()
            print(speech.get('text') or '', end='')
            while True:
                if speech['status'] == 'error':
                    break
                if speech['status'] == 'void':
                    self.voids += 1
                    break
                text = speech['text']
                cmd, params = Command.reg_find(text).values()
                try:    response = cmd.start(params)
                except: break
                self.reply(response)
                self.check_threads()
                self.report()
                if response.callback:
                    speech = recognize(response.callback, {})
                else:
                    break

    def recognize(self, callback, params):
        print('\nYou: ', end='')
        speech = self.listener.listen()
        if speech['status'] in ['error', 'void']:
            return speech
        text = speech['text']
        print(text, end='')
        while True:
            self.check_threads()
            if not callback: break
            try:
                if response := callback.answer(text):
                    self.reply(response)
            except:
                break
            self.memory.insert(0, {
                'text': text,
                'cmd':  cmd,
                'response': response,
            })
            speech = recognize(response.callback, params)
            if callback.once: break
        return speech

    def report(self):
        for response in self.reports:
            if response.voice:
                self.voice.generate(response.voice).speak()
            time.sleep(2)
        self.reports = []

    def reply(self, response):
        if response.text:                                #   print answer
            print('\nArchie: '+response.text)
        if response.voice:                               #   say answer
            self.voice.generate(response.voice).speak()
        if response.thread:                              #   add background thread to stack
            self.threads.append(response.thread)

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
