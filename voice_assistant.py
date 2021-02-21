#!/usr/local/bin/python3.8
import SpeechRecognition
import Text2Speech
from Command import Command
import config
import modules
import os

listener = SpeechRecognition.SpeechToText()
voice    = Text2Speech.Engine()
threads  = []
reports  = []
memory   = []
voids    = 0

if config.double_clap_activation:
    # check double clap from arduino microphone module
    def checkClap(channel):
        global lastClapTime
        global doubleClap
        now = time.time()
        delta = now - lastClapTime
        if 0.1 < delta < 0.6:
            doubleClap = True
        else:
            lastClapTime = now

    # waiting for double clap
    def sleep():
        global lastClapTime
        lastClapTime = 0
        global doubleClap
        while not doubleClap:
            check_threads()
            time.sleep(1)
        else:
            doubleClap = False

    import RPi.GPIO as GPIO
    import time
    lastClapTime = 0
    doubleClap = False
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(12, GPIO.IN)
    GPIO.add_event_detect(12, GPIO.RISING, callback=checkClap)

def check_threads():
    for thread in threads:
        if not thread['finish_event'].is_set(): continue
        response = thread['thread'].join()
        reply(response)
        if response.callback:
            if response.callback.quiet:
                response.callback.start()
            else:
                for _ in range(3):
                    print('\nYou: ', end='')
                    speech = listener.listen()
                    if speech['status'] == 'ok':
                        print(speech['text'], '\n')
                        new_response = response.callback.answer(speech['text'])
                        reply(new_response)
                        break
                else:
                    reports.append(response)
        thread['finish_event'].clear()
        del thread

def report():
    global reports
    for response in reports:
        if response.voice:
            voice.generate(response.voice).speak()
        time.sleep(2)
    reports = []

def reply(response):
    if response.text:                                #   print answer
        print('\nArchie: '+response.text)
    if response.voice:                               #   say answer
        voice.generate(response.voice).speak()
    if response.thread:                              #   add background thread to stack
        threads.append(response.thread)

def recognize(callback, params):
    print('\nYou: ', end='')
    speech = listener.listen()
    if speech['status'] in ['error', 'void']:
        return speech
    text = speech['text']
    print(text, end='')
    while True:
        check_threads()
        if not callback: break
        try:
            if response := callback.answer(text):
                reply(response)
        except:
            break
        memory.insert(0, {
            'text': text,
            'cmd':  cmd,
            'response': response,
        })
        speech = recognize(response.callback, params)
        if callback.once: break
    return speech

listener.listen_noise()
os.system('clear')

while True:
    if voids >= 3:
        voids = 0
        if config.double_clap_activation:
            print('\nSleep (-_-)zzZZ\n')
            sleep()
    print('\nYou: ', end='')
    speech = listener.listen()
    print(speech.get('text') or '', end='')
    voids = 0
    while True:
        if speech['status'] == 'error':
            break
        if speech['status'] == 'void':
            voids += 1
            break
        text = speech['text']
        cmd, params = Command.reg_find(text).values()
        try:    response = cmd.start(params)
        except: break
        reply(response)
        check_threads()
        report()
        if response.callback:
            speech = recognize(response.callback, {})
        else:
            break
