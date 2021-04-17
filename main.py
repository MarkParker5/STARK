#!/usr/local/bin/python3.8
import os
import config

os.system('git pull')

modules = {
    'Voice Assistant':  'voice_assistant',
    'Telegram bot':     'telegram_bot',
}

for name, module in modules.items():
    try:
        print(f'launching the {name}')
        os.system(f'lxterminal --command="python3.8 {config.path}/{module}.py & read"')
    except:
        print(f'[error]\t{name} launch failed')

print('Running server...')
os.system(f'lxterminal --command="python3.8 {config.path}/manage.py runserver 192.168.0.129:8000 & read"')
os.system(f'lxterminal --command="vlc"')
