#!/usr/local/bin/python3.8
import os
import config
import RPi.GPIO as GPIO
import time

modules = {
    'Voice Assistant':  'voice_assistant',
    'Telegram bot':     'telegram_bot',
}

for name, module in modules.items():
    try:
        print(f'launching the {name}')
        os.system(f'lxterminal --command="python3.8 {config.path}/{module}.py"')
    except:
        print(f'[error]\t{name} launch failed')

def launch_vc():
    try:
        print('Voice Assistant activation...')
        os.system(f'lxterminal --command="python3.8 {config.path}/voice_assistant.py"')
    except:
        print(f'[error]\tlaunch failed')

if config.double_clap_activation:
    lastClapTime = 0

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(12, GPIO.IN)

    def callback(channel):
        global lastClapTime
        now = time.time()
        delta = now - lastClapTime
        if 0.1 < delta < 0.6:
            lauch_vc()
        else:
            lastClapTime = now

    GPIO.add_event_detect(12, GPIO.RISING, callback=callback)
    while True: time.sleep(1)
