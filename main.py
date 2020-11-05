#!/usr/local/bin/python3.8
import os
import config

modules = {
    'Voice Assistant':  'voice_assistant',
    'Telegram bot':     'telegram_bot',
}

for name, module in modules.items():
    try:
        print(f'launching the {name}')
        os.system(f'nohup {config.path}/{module}.py &')
    except:
        print(f'[error]\t{name} launch failed')
