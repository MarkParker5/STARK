from .SmartHome import SmartHome
from Command import Command, Response

################################################################################

@Command.new(['(открыть|открой) (окно|окна)', ' подними|поднять) (шторы|роллеты)'])
def windowOpen(params):
    SmartHome.send({
        'target': 'window',
        'cmd':  'window_open',
    })
    voice = text = ''
    return Response(text = text, voice = voice)

################################################################################

@Command.new(['(закрыть|закрой) (окно|окна)', '(опусти|опустить) (шторы|роллеты)'])
def windowClose(params):
    SmartHome.send({
        'target': 'window',
        'cmd':  'window_close',
    })
    voice = text = ''
    return Response(text = text, voice = voice)
