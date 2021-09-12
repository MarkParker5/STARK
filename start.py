#!/usr/local/bin/python3.8
# entry point
import multiprocessing

import Controls
import Features

# TODO:
# import subprocess
# start oll controls in own thread or subprocess:
# voice assistant, telegram bot, django(api and ui)

telegram = multiprocessing.Process(target = Controls.TelegramBot().start)
voiceAssistant = multiprocessing.Process(target = Controls.VoiceAssistant().start)

telegram.start()
voiceAssistant.start()

# telegram.join()
# voiceAssistant.join()
