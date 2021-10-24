from .SmartHome import *
from ArchieCore import Response
################################################################################

def method(params):
    SmartHome.send({
        'target': 'main_light',
        'cmd':  'light_on',
    })
    voice = text = ''
    return Response(text = text, voice = voice)

patterns = ['* (включ|выключ)* свет *']
main_light = SmartHome('main_light', patterns)
main_light.setStart(method)

################################################################################
#       led

def method(params):
    SmartHome.send({
        'target': 'led',
        'cmd':  'led_on',
    })
    voice = text = ''
    return Response(text = text, voice = voice)

patterns = ['* включи* подсветку *']
light_on = SmartHome('led_on', patterns)
light_on.setStart(method)

################################################################################

def method(params):
    SmartHome.send({
        'target': 'led',
        'cmd':  'led_off',
    })
    voice = text = ''
    return Response(text = text, voice = voice)

patterns = ['* выключи* подсветку *']
led_off = SmartHome('led_off', patterns)
led_off.setStart(method)

################################################################################

def method(params):
    SmartHome.send({
        'target': 'led',
        'cmd':  'led_hello',
    })
    voice = text = ''
    return Response(text = text, voice = voice)

patterns = []
led_hello = SmartHome('led_hello', patterns)
led_hello.setStart(method)

################################################################################
