# !/usr/local/bin/python3.8
# entry point

import os, sys
import multiprocessing
import uvicorn

import Features
import Controls
from Controls.API.main import app


def start_api():
    uvicorn.run('start:app')

def multiprocess():
    controls = [
        Controls.VoiceAssistant(),
        Controls.TelegramBot(),
    ]

    starts = [control.start for control in controls]
    starts.append(start_api)

    processes = []
    for start in starts:
        process = multiprocessing.Process(target = start)
        process.start()
        processes.append(process)

    for process in processes:
        process.join()

def multiterminal():
    controls = {
        'VoiceAssistant': Controls.VoiceAssistant().start,
        'TelegramBot': Controls.TelegramBot().start,
        'API': start_api,
    }

    if len(sys.argv) > 1:
        controls.get(sys.argv[1])()
    else:
        for key in controls.keys():
            os.system(f'lxterminal --command="python start.py {key}"')

if __name__ == '__main__': multiprocess()
