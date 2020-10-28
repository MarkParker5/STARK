#   Abstract class Command
#
#   Command                 - parent of all command classes
#   command                 - object (class instance)
#   Command.list            - list of all commands
#   Command.find()          - recognize command from a string by fuzzywuzzy, return command object
#       must return dict like {'cmd': cmd, 'params': params}
#   Command.reg_find()      - recognize command from a string with regexe patterns, return command object
#       must return dict like {'cmd': cmd, 'params': params}
#   this                    - object (class instance) pointer (self)
#   abstract this.start()   - required method for all commands
#   this.keywords           - dictionary of arrays keywords
#       like {
#           (int)weight  : ['word1', 'word2', 'word3'],
#           (int)weight1 : ['word3', 'word4'],
#           (int)weight2 : ['word5', 'word6', 'word7', 'word8', 'word9'],
#       }
#   this.patterns           - list of command patterns
#   this.subpatterns        - list of subpaterns (context patterns)
#       like ['* который * час *', '* скольк* * (врем|час)* *']
#   Command._entities       - linked patterns   $Pattern
#   Command.regex           - regex patterns dict for better syntax
#
#
#



from abc import ABC, abstractmethod                     #   for abstract class and methods
from fuzzywuzzy import fuzz
from threading import Thread, Event
import re

class RThread(Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self, *args, **kwargs):
        super().join(*args, **kwargs)
        return self._return

class Command(ABC):
    _list     = []                                           #   list of all commands
    _entities = {
        'word':   lambda: r'\b[A-Za-zА-ЯЁа-яё0-9\-]+\b',
        'text':   lambda: r'[A-Za-zА-ЯЁа-яё0-9\- ]+',
        'quest' : lambda: Command.compilePattern('(кто|что|как|какой|какая|какое|где|зачем|почему|сколько|чей|куда|когда)'),
        'repeat': lambda: Command.compilePattern('* ((повтор*)|(еще раз)|(еще*раз)*) *'),
    }
    _regex    = {
        #   stars   *
        '([A-Za-zА-ЯЁа-яё0-9\(\)\[\]\{\}]+)\*([A-Za-zА-ЯЁа-яё0-9\(\)\[\]\{\}]+)':  r'\\b\1.*\2\\b',  #   'te*xt'
        '\*([A-Za-zА-ЯЁа-яё0-9\(\)\[\]\{\}]+)':          r'\\b.*\1',                            #   '*text'
        '([A-Za-zА-ЯЁа-яё0-9\(\)\[\]\{\}]+)\*':          r'\1.*\\b',                            #   'text*'
        '(^|\s)\*($|\s)':      r'.*',                                                      #   '*'     ' * '
        #   one of the list      (a|b|c)
        '\(((?:.*\|)*.*)\)':    r'(?:\1)',
        #   0 or 1 the of list [abc]
        '\[((?:.*\|?)*?.*?)\]': r'(?:\1)??',
        #   one or more of the list, without order     {a|b|c}
        '\{((?:.*\|?)*?.*?)\}': r'(?:\1)+?',
    }
    def __init__(this, name, keywords = {}, patterns = [], subPatterns = []):                 #   initialisation of new command
        this._name          = name
        this._keywords      = keywords
        this._patterns      = patterns
        this._subPatterns   = subPatterns
        Command.append(this)

    def __str__(this):
        str = f'{this.__class__.__name__}.{this.getName()}:\n'
        for key, value in this._keywords.items():
            str += f'\t{key}:\t{value}\n'
        return str

######################################################################################
#                            CONTROL KEYWORDS                                        #
######################################################################################
    def getKeyword(this, string):                                  #   return position of the keyword
        for weight, array in this._keywords.items():
            index = 0
            for word in array:
                if string == word:
                    return (weight, index)
                index += 1
        return None #   if not found

    def removeKeyword(this, string):
        position = this.getKeyword(string)
        if(position): del this._keywords[ position[0] ][ position[1] ]

    def addKeyword(this, weight, string):                           #   add new keywords to end of the list
        if this.getKeyword(string): return
        if( this._keywords.get(weight) ):   this._keywords[weight].append(string)
        else:                               this._keywords[weight] = [string]

    def changeKeyword(this, weight, name):                          #   set new weight to keyword   (find by name)
        this.removeKeyword(name)
        this.addKeyword(weight, name)

    def checkContext(this, string):                                 #   return cmd if the string matches the cmd context
        for pattern in this.getSubPatterns():
            if match := re.search(re.compile(Command.compilePattern(pattern)), string):
                return {
                'cmd': this,
                'params': {**match.groupdict(), 'string':string},   #   return parans+initial text
            }
        raise Exception("Not Found")                                #   raise exception if context not found

######################################################################################
#                                     SETTERS                                        #
######################################################################################
    def setStart(this, function):                                   #   define start    (required)
        this.start = function

######################################################################################
#                                     GETTERS                                        #
######################################################################################
    def getName(this):
        return this._name

    def getKeywords(this):
        return this._keywords

    def getPatterns(this):
        return this._patterns

    def getSubPatterns(this):
        return this._subPatterns

######################################################################################
#                               ABSTRACT METHODS                                     #
######################################################################################
    @abstractmethod
    def start(this, params):                    #   main method
        pass

######################################################################################
#                                 STATIC METHODS                                     #
######################################################################################
    @staticmethod
    def getList():
        return Command._list                    # all commands

    @staticmethod
    def getRegexDict():
        return Command._regex                   # all standart patterns

    @staticmethod
    def getEntity(key):
        entity = Command._entities.get(key)     # all linked $Pattern s
        return entity()

    @staticmethod
    def append(obj):                            # add new command to list
        Command._list.append(obj)

    @staticmethod
    def getCommand(name):                       # get command by name
        for obj in Command.getList():
            if obj.getName() == name: return obj

    @staticmethod
    def isRepeat(string):                       # return True if command is repeat-cmd
        if re.search(re.compile(Command.getEntity('repeat')), string): return True
        return False

    @staticmethod
    def ratio(string, word):                    # get average distance of string and pattern
        return ( fuzz.WRatio(string, word) + fuzz.ratio(string, word) ) / 2

    @staticmethod
    def compilePattern(pattern):                # transform my syntax to standart regexp
        #   transform patterns to regexp
        for ptrn, regex in Command.getRegexDict().items():
            pattern = re.sub(re.compile(ptrn), regex, pattern)
        #   find and replace links like  $Pattern
        link = re.search(re.compile('\$[a-z]+'), pattern)
        if link: pattern = re.sub('\\'+link[0], f'(?P<{link[0][1:]}>{Command.getEntity( link[0][1:] )})', pattern)
        #   return compiled regexp
        return pattern

    @staticmethod
    def find(string):                               # find command by fuzzywuzzy
        string = string.lower()
        chances = {}
        list = Command.getList()
        #   calculate chances of every command
        for i, obj in enumerate( list ):
            chances[i] = 0
            k = 1 / ( sum( [int(w)*len(kw) for w, kw in obj.getKeywords().items()] ) or 1 )
            for weight, kws in obj.getKeywords().items():
                for kw in kws:
                    chances[i] += Command.ratio(string, kw) * weight * k
        #    find command with the biggest chance
        if( sum( chances.values() ) ):
            top = max( chances.values() ) / sum( chances.values() ) * 100
        else: # if all chances is 0
            return {
                'cmd': Command.QA,
                'params': {'string':string,},
            }
        #if( max( chances.values() ) < 800 or top < 50): return list[0]
        #   find top command obj
        for i, chance in chances.items():
            if chance == max( chances.values() ):
                return {
                    'cmd': Command.QA, #dialog mode
                    'params': {'string':string,},
                }

    @staticmethod
    def reg_find(string):                       # find comman by pattern
        string = string.lower()
        list   = Command.getList()
        if not string: return {
            'cmd': Command.getCommand('Hello'),
            'params': {'string':string,},
        }
        #   find command obj by pattern
        for obj in list:
            for pattern in obj.getPatterns():
                if match := re.search(re.compile(Command.compilePattern(pattern)), string):
                    return {
                    'cmd': obj,
                    'params': {**match.groupdict(), 'string':string,},
                }
        #   return Question-Answer system if command not found
        return {
            'cmd': Command.QA,
            'params': {'string':string,},
        }

    @staticmethod
    def background(answer = '', voice = ''):    # make background cmd
        def decorator(cmd): #wrapper of wrapper (decorator of decorator)
            def wrapper(text):
                finish_event  = Event()
                thread        = RThread(target=cmd, args=(text, finish_event))
                thread.start()
                return {
                    'type': 'background',
                    'text': answer,
                    'voice': voice,
                    'thread': {
                        'thread': thread,
                        'finish_event': finish_event,
                        }
                }
            return wrapper
        return decorator
