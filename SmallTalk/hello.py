from .SmallTalk import *
from Command import Response
################################################################################
def method(params):
    voice = text = 'Привет'
    return Response(text = text, voice = voice)

patterns = ['* привет* *',]
hello = SmallTalk('Hello', {}, patterns)
hello.setStart(method)
