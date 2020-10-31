from .SmallTalk import *
################################################################################
def method(params):
    voice = text = 'Привет'
    return {
        'type': 'simple',
        'text': text,
        'voice': voice,
    }

patterns = ['* привет* *',]
hello = SmallTalk('Hello', {}, patterns)
hello.setStart(method)
