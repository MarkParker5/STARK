#   Abstract class Command
#   Command                 - parent of all command classes
#   command                 - object (class instance)
#   Command.list            - list of all commands
#   Command.find()          - recognize command from a string, return command object
#   this                    - object (class instance) pointer
#   abstract this.start()   - required method for all commands
#   abstract this.confirm() - Return True/False (User responce)
#   this.keywords           - dictionary of arrays keywords
#       like {
#           (int)weight  : ['word1', 'word2', 'word3'],
#           (int)weight1 : ['word3', 'word4'],
#           (int)weight2 : ['word5', 'word6', 'word7', 'word8', 'word9'],
#       }
#

from abc import ABC, abstractmethod                     #   for abstract class and methods
from fuzzywuzzy import fuzz

class Command(ABC):
    _list = []                                           #   list of all commands
    def __init__(this, name, keywords):                 #   initialisation of new command
        this._name = name
        this._keywords = keywords
        Command.append(this)

    def __str__(this):
        str = f'{this.__class__.__name__}.{this.getName()}:\n'
        for key, value in this._keywords.items():
            str += f'\t{key}:\t{value}\n'
        return str

    #   control keywords
    def _getKeyword(this, string):                      #   return position of keyword
        for weight, array in this._keywords.items():
            index = 0
            for word in array:
                if string == word:
                    return (weight, index)
                index += 1
        return None #   if not found

    def removeKeyword(this, string):
        position = this._getKeyword(string)
        if(position): del this._keywords[ position[0] ][ position[1] ]

    def addKeyword(this, weight, string):
        if this._getKeyword(string): return
        if( this._keywords.get(weight) ):   this._keywords[weight].append(string)
        else:                           this._keywords[weight] = [string]

    def changeKeyword(this, weight, string):
        this.removeKeyword(string)
        this.addKeyword(weight, string)

    #   setters
    def setStart(this, function):               #   define start    (required)
        this.start = function

    def setConfirm(this, function):             #   define confirm (optional)
        this.confirm = function

    #   getters
    def getName(this):
        return this._name

    def getKeywords(this):
        return this._keywords

    #   abstract
    @abstractmethod
    def start(this, string):                #   main method
        pass

    @abstractmethod
    def confirm(this):                      #   optional method
        pass

    #   static
    @staticmethod
    def getList():
        return Command._list

    @staticmethod
    def append(obj):
        Command._list.append(obj)

    @staticmethod
    def ratio(string, word):
        return ( fuzz.WRatio(string, word) + fuzz.ratio(string, word) ) / 2

    @staticmethod
    def find(string):
        string = string.lower()
        chances = {}
        list = Command.getList()
        for i, obj in enumerate( list ):
            chances[i] = 0
            for weight, words in obj.getKeywords().items():
                for word in words:
                    chances[i] += Command.ratio(string, word) * weight
        if( sum( chances.values() ) ):
            top = max( chances.values() ) / sum( chances.values() ) * 100
        else:
            return list[0]
        if( max( chances.values() ) < 1000 or top < 80): return list[0]
        print(chances)
        print(top)
        for i, chance in chances.items():
            if chance == max( chances.values() ):
                return list[i]
