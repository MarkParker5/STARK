#!/usr/local/bin/python3.8
# entry point

import multiprocessing
import Controls

# TODO:
# start oll controls in own thread or subprocess:
# voice assistant, telegram bot, django(api and ui)

def main():
    controls = [
        Controls.VoiceAssistant(),
        Controls.TelegramBot(),
        Controls.RemoteControl(),
        Controls.Django(),
    ]

    processes = []
    for control in controls:
        process = multiprocessing.Process(target = control.start)
        process.start()

    for process in processes:
        process.join()

if __name__ =='__main__': main()
