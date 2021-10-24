from .Raspi import *
import os
from ArchieCore import CommandsManager, Callback, Response
import config
################################################################################
def reboot(params):
    if params['bool']:
        os.system('sudo reboot')
    return Response(text = '', voice = '')

reboot_cb = Callback(['$bool',])
reboot_cb.setStart(reboot)

@CommandsManager.background(answer = 'Проверяю обновления...', voice = 'Проверяю обновления')
def method(params, finish_event):
    os.system('git -C '+config.path+' remote update')
    if not 'git pull' in os.popen('git -C '+config.path+' status -uno').read():
        finish_event.set()
        voice = text = 'Установлена последняя версия'
        return Response(text = text, voice = voice)
    os.system('git -C '+config.path+' pull')
    finish_event.set()
    voice = text = 'Обновления скачаны. Перезагрузиться?'
    return Response(text = text, voice = voice, callback = reboot_cb)

patterns = ['* обновись *', '* можешь обновиться *', '* обнови себя *', '* скачай обновлени* *', '* провер* обновлени* *']
gitpull = Raspi('git pull archie.git', patterns)
gitpull.setStart(method)
