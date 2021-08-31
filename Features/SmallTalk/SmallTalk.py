#   Create class SmallTalk
#   Is child of Command
#   Module for speaking with voice assistent
#   See class Command

from ..Command import Command                     #   import parent class

class SmallTalk(Command):
    def start(self, string):                    #   main method
        print(f'Hello, {string=}')
