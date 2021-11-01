from .Raspi import Raspi
import os
from ArchieCore import Command, CommandsManager, Response
import config

################################################################################

@Command.new(['$bool'], primary = False)
def reboot(params):
    if params['bool']:
        os.system('sudo reboot')
    return Response(text = '', voice = '')

################################################################################

@Command.new([
    'обновись',
    'можешь обновиться',
    'обнови себя',
    'скачай обновлени*',
    'провер* обновлени*'])
@CommandsManager.background(answer = 'Проверяю обновления...', voice = 'Проверяю обновления')
def gitpull(params, finish_event):
    os.system('git -C '+config.path+' remote update')
    if not 'git pull' in os.popen('git -C '+config.path+' status -uno').read():
        finish_event.set()
        voice = text = 'Установлена последняя версия'
        return Response(text = text, voice = voice)
    os.system('git -C '+config.path+' pull')
    finish_event.set()
    voice = text = 'Обновления скачаны. Перезагрузиться?'
    return Response(text = text, voice = voice, context = [reboot,])
