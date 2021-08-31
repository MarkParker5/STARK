from .Command import Command
from .Response import Response
import re

class Callback:
    def __init__(self, patterns, quiet = False, once = True):
        self.patterns = patterns
        self.quiet = quiet
        self.once = once

    def setStart(self, function):
        self.start = function

    def start(self, params):
        pass

    def answer(self, string):
        for pattern in self.patterns:
            if match := re.search(re.compile(Command.compilePattern(pattern)), string):
                return self.start({**match.groupdict(), 'string':string})
        return None

    @staticmethod
    def background(answer = '', voice = ''):
        def decorator(cmd):
            def wrapper(text):
                finish_event  = Event()
                thread        = RThread(target=cmd, args=(text, finish_event))
                thread.start()
                return Response(voice = voice, text = answer, thread = {'thread': thread, 'finish_event': finish_event} )
            return wrapper
        return decorator
