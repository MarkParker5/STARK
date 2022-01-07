# !/usr/local/bin/python3.8
# entry point

import os, sys
import multiprocessing

import Features
import Controls

def multiprocess():
    controls = [
        Controls.VoiceAssistant(),
        Controls.TelegramBot(),
        #RemoteControl(),
        #Django(),
    ]

    processes = []
    for control in controls:
        process = multiprocessing.Process(target = control.start)
        process.start()

    for process in processes:
        process.join()

def multiterminal():
    controls = {
        'VoiceAssistant': Controls.VoiceAssistant,
        'TelegramBot': Controls.TelegramBot
    }

    if len(sys.argv) > 1:
        controls.get(sys.argv[1])().start()
    else:
        for key in controls.keys():
            os.system(f'lxterminal --command="python start.py {key}"')

if __name__ == '__main__': multiterminal()
