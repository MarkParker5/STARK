#!/usr/local/bin/python3.8
# entry point

import multiprocessing
import Controls

# TODO:
# start oll controls in own thread or subprocess:
# voice assistant, telegram bot, django(api and ui)

def main():
    telegram = multiprocessing.Process(target = Controls.TelegramBot().start)
    voiceAssistant = multiprocessing.Process(target = Controls.VoiceAssistant().start)

    telegram.start()
    #voiceAssistant.start()

    telegram.join()
    #voiceAssistant.join()

if __name__ =='__main__': main()
    
