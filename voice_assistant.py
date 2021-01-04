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
memory   = []
voids    = 0

listener.listen_noise()

if config.double_clap_activation:
    # check double clap from arduino microphone module
    def checkClap(channel):
        global lastClapTime
        now = time.time()
        delta = now - lastClapTime
        if 0.1 < delta < 0.6:
            doubleClap = True
        else:
            lastClapTime = now

    # waiting for double clap
    def sleep():
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

def reply(responce):
    if responce['text']:                                #   print answer
        print('Archie: '+responce['text'])
    if responce['voice']:                               #   say answer
        voice.generate(responce['voice']).speak()
    if responce['type'] == 'background':                #   add background thread to list
        threads.append(responce['thread'])

def check_threads():
    for thread in threads:
        if thread['finish_event'].is_set():
            responce = thread['thread'].join()
            reply(responce)
            thread['finish_event'].clear()
            del thread

os.system('clear')
while True:                                             #    main loop
    check_threads()
    print('\nYou: ', end='')
    # input
    speech = listener.listen()
    text   = speech['text']
    if speech['status'] == 'ok':
        print(text)
        voids = 0
        # repeat last answer
        if Command.isRepeat(text):
            reply(memory[0]['responce']);
            continue
        # recognize command with context
        try:
            cmd, params = memory[0]['cmd'].checkContext(text).values()
            if memory[0].get('params'): params = {**memory[0].get('params'), **params}
        except:
            cmd, params = Command.reg_find(text).values()
        # execute command
        responce = cmd.start(params)
        # say answer
        reply(responce)
        # waiting answer on question
        if responce['type'] == 'question':
            print('\nYou: ', end='')
            speech = listener.listen()
            if speech['status'] == 'ok':
                text = speech['text']
                print(text)
                if responce := responce['callback'].answer(text): reply(responce)
        # remember the command
        memory.insert(0, {
            'text': text,
            'cmd':  cmd,
            'responce': responce,
        })
    else:
        if speech['status'] == 'error': print('Отсутсвует подключение к интернету');
        elif speech['status']  == 'void': voids += 1;
        if voids >= 3:
            voids = 0
            if config.double_clap_activation:
                print('Sleep (-_-)zzZZ')
                sleep()
