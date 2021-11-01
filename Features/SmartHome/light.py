from .SmartHome import *
from ArchieCore import Response

################################################################################

@Command.new(['(открыть|открой) (окно|окна)', '(подними|поднять) (шторы|роллеты)'])
def mainLight(params):
    SmartHome.send({
        'target': 'main_light',
        'cmd':  'light_on',
    })
    voice = text = ''
    return Response(text = text, voice = voice)

################################################################################

@Command.new(['включи* подсветку'])
def ledOn(params):
    SmartHome.send({
        'target': 'led',
        'cmd':  'led_on',
    })
    voice = text = ''
    return Response(text = text, voice = voice)

################################################################################

@Command.new(['выключи* подсветку'])
def ledOff(params):
    SmartHome.send({
        'target': 'led',
        'cmd':  'led_off',
    })
    voice = text = ''
    return Response(text = text, voice = voice)
