from .SmartHome import *

################################################################################

def method(params):
    SmartHome.send({
        'target': 'window',
        'cmd':  'window_open',
    })
    voice = text = 'Поднимаю роллеты'
    return {
        'type': 'simple',
        'text': text,
        'voice': voice,
    }

keywords = {}
patterns = ['* (открыть|открой) (окно|окна) *', '* (подними|поднять) (шторы|роллеты) *']
window_open = SmartHome('window_open', keywords, patterns)
window_open.setStart(method)

################################################################################

def method(params):
    SmartHome.send({
        'target': 'window',
        'cmd':  'window_close',
    })
    voice = text = 'Опускаю роллеты'
    return {
        'type': 'simple',
        'text': text,
        'voice': voice,
    }

keywords = {}
patterns = ['* (закрыть|закрой) (окно|окна) *', '* (опусти|опустить) (шторы|роллеты) *']
window_close = SmartHome('window_close', keywords, patterns)
window_close.setStart(method)
