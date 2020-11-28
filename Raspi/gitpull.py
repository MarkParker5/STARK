from .Raspi import *
import os
from Command import Callback
import config
################################################################################
def reboot(params):
    if params['bool']:
        os.system('sudo systemctl restart archie')
    return {
        'text': 'Хорошо',
        'voice': 'Хорошо',
        'type': 'simple',
    }

reboot_cb = Callback(['$bool',])
reboot_cb.setStart(reboot)

@Raspi.background(answer = 'Проверяю обновления...', voice = 'Проверяю обновления')
def method(params, finish_event):
    os.system('git -C '+config.path+' remote update')
    if not 'git pull' in os.popen('git -C '+config.path+' status -uno').read():
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

patterns = ['* обновись *', '* можешь обновиться *', '* обнови себя *', '* скачай обновлени* *', '* провер* обновлени* *']
gitpull = Raspi('git pull archie.git', [], patterns)
gitpull.setStart(method)
