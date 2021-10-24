from typing import Type
from . import Command
from ..Pattern import ACObject

class SearchResult:
    command: Command
    parameters: dict[str, ACObject]

    def __init__(self, command: Command, parameters: dict[str, ACObject] = {}):
        self.command = command
        self.parameters = parameters

class CommandsManager:
    allCommands: list[Command] = []

    def __new__(cls):                                                           # Singleton
        if not hasattr(cls, 'instance'):
            cls.instance = super().__new__(cls)
        return cls.instance

    def search(self, string) -> list[SearchResult]:                             # find command by pattern
        string = string.lower()
        results: list[SearchResult] = []
        acstring = ACString(string)

        #   find command obj by pattern
        for command in self.allCommands:
            for pattern in command.patterns:
                if groupdict := pattern.match(string):
                    parameters: dict[str: ACObject] = {'string': acstring,}
                    for key, value in groupdict.items():
                        name, typeName = key.split(':')
                        ACType: Type[ACObject] = CommandsManager.classFromString(typeName)
                        parameters[name] = ACType(value)
                    results.append(SearchResult(command, parameters))

        if results: return results
        else: return [SearchResult(Command.QA, {'string': acstring,}),]

    def append(self, obj):                                                      # add new command to list
        self.allCommands.append(obj)

    def getCommand(name):                                                       # TODO: quick search
        for command in self.allCommands:
            if command.name == name: return command

    @staticmethod
    def classFromString(className: str) -> ACObject:
        return getattr(sys.modules[__name__], className)

    @staticmethod
    def background(answer = '', voice = ''):                                    # make background cmd
        def decorator(func):
            def wrapper(text):
                finishEvent = Event()
                thread = RThread(target=func, args=(text, finish_event))
                thread.start()
                return Response(voice = voice, text = answer, thread = ThreadData(thread, finishEvent) )
            return wrapper
        return decorator
