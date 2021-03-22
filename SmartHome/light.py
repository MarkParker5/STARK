from .SmartHome import *
from Command import Response
################################################################################

def method(params):
    SmartHome.send({
        'target': 'main_light',
        'cmd':  'light_on',
    })
    voice = text = ''
    return Response(text = text, voice = voice)

keywords = {}
patterns = ['* (включ|выключ)* свет *']
main_light = SmartHome('main_light', keywords, patterns)
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

keywords = {}
patterns = ['* включи* подсветку *']
light_on = SmartHome('led_on', keywords, patterns)
light_on.setStart(method)

################################################################################

def method(params):
    SmartHome.send({
        'target': 'led',
        'cmd':  'led_off',
    })
    voice = text = ''
    return Response(text = text, voice = voice)

keywords = {}
patterns = ['* выключи* подсветку *']
led_off = SmartHome('led_off', keywords, patterns)
led_off.setStart(method)

################################################################################

def method(params):
    SmartHome.send({
        'target': 'led',
        'cmd':  'led_hello',
    })
    voice = text = ''
    return Response(text = text, voice = voice)

keywords = {}
patterns = []
led_hello = SmartHome('led_hello', keywords, patterns)
led_hello.setStart(method)

################################################################################
