from .SmartHome import *
from Command import Response
################################################################################

def method(params):
    SmartHome.send({
        'target': 'window',
        'cmd':  'window_open',
    })
    voice = text = ''
    return Response(text = text, voice = voice)

patterns = ['* (открыть|открой) (окно|окна) *', '* (подними|поднять) (шторы|роллеты) *']
window_open = SmartHome('window_open', patterns)
window_open.setStart(method)

################################################################################

def method(params):
    SmartHome.send({
        'target': 'window',
        'cmd':  'window_close',
    })
    voice = text = ''
    return Response(text = text, voice = voice)

patterns = ['* (закрыть|закрой) (окно|окна) *', '* (опусти|опустить) (шторы|роллеты) *']
window_close = SmartHome('window_close', patterns)
window_close.setStart(method)
