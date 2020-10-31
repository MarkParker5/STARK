from .Command import Command
import re

class Callback:
    def __init__(this, patterns):
        this.patterns = patterns

    def setStart(this, function):
        this.start = function

    def start(this, params):
        pass

    def answer(this, string):
        for pattern in this.patterns:
            if match := re.search(re.compile(Command.compilePattern(pattern)), string):
                return this.start({**match.groupdict(), 'string':string})   
        return None
