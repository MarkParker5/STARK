from .SmartHome import *
from ..Command import Response
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
