from .SmallTalk import *
from ArchieCore import Response
################################################################################

@SmallTalk.new('Hello', patterns = ['* привет* *',])
def method(params):
    voice = text = 'Привет'
    return Response(text = text, voice = voice)
