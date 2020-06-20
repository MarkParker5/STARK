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



from abc import ABC, abstractmethod         #   for abstract class and methods

class Command(ABC):
    list = []                               #   list of all commands
    def __init__(this, name, keywords):     #   initialisation of new command
        this.name = name
        this.keywords = keywords
        Command.list.append(this)

    def _get_kw(this, string):
        for weight, array in this.keywords.items():
            index = 0
            for word in array:
                if string == word:
                    return (weight, index)
                index += 1
        return None

    def remove_kw(this, string):
        position = this._get_kw(string)
        if(position):
            del this.keywords[ position[0] ][ position[1] ]
    def add_kw(this, weight, string):
        if( this.keywords[weight] ):    this.keywords[weight].append(string)
        else:                           this.keywords[weight] = [string]

    #   static
    @staticmethod
    def find(string):
        print('Find: '+string)
    #   abstract
    @abstractmethod
    def start(this, string):                #   main method
        pass
    @abstractmethod
    def confirm(this):                      #   optional method
        pass
