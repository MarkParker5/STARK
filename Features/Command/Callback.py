from .Command import Command
from .Response import Response
import re

class Callback:
    def __init__(this, patterns, quiet = False, once = True):
        this.patterns = patterns
        this.quiet = quiet
        this.once = once

    def setStart(this, function):
        this.start = function

    def start(this, params):
        pass

    def answer(this, string):
        for pattern in this.patterns:
            if match := re.search(re.compile(Command.compilePattern(pattern)), string):
                return this.start({**match.groupdict(), 'string':string})
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
