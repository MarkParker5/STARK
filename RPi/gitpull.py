from .RPi import *
import os
from Command import Callback
import config
################################################################################
def reboot(params):
    if params['bool']:
        os.system('sudo reboot')
    return {
        'text': 'Хорошо',
        'voice': 'Хорошо',
        'type': 'simple',
    }

reboot_cb = Callback(['$text',])
reboot_cb.setStart(reboot)

@RPi.background(answer = 'Проверяю обновления...', voice = 'Проверяю обновления')
def method(params, finish_event):
    os.system('git -C '+config.path+' remote update')
    if not 'git pull' in os.popen('git -C '+config.path+' status -uno').readline():
        finish_event.set()
        return {
            'text': 'Установлена последняя версия',
            'voice': 'Установлена последняя версия',
            'type': 'simple',
        }
    os.system('git -C '+config.path+' pull')
    finish_event.set()
    return {
        'text': 'Обновления скачаны. Перезагрузиться?',
        'voice': 'Обновления скачаны. Перезагрузиться?',
        'type': 'question',
        'callback': reboot_cb,
    }

patterns = ['* обновись *', '* можешь обновиться *', '* обнови себя *', '* скачай обновления *']
gitpull = RPi('git pull archie.git', [], patterns)
gitpull.setStart(method)

#

[Unit]
Description=A.R.C.H.I.E.

[Service]
WorkingDirectory=/home/pi/archie
ExecStart=/home/pi/archie/main.py
Restart=always
RestartSec=10
KillSignal=SIGINT
SyslogIdentifier=archie

[Install]
WantedBy=multi-user.target
