# !/usr/local/bin/python3.8
# entry point

import multiprocessing

import Features
import Controls

def main():
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

if __name__ == '__main__': main()
