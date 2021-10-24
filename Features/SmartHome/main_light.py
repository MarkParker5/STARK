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
