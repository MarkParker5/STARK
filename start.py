#!/usr/local/bin/python3.8
# entry point

import Controls
import Features

# TODO:
# import subprocess
# start oll controls in own thread or subprocess:
# voice assistant, telegram bot, django(api and ui)

Controls.TelegramBot().start()
#Controls.VoiceAssistant().start()
