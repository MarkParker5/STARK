#   Create class SmallTalk
#   Module for speaking with voice assistent
#   Command is parent for SmallTalk
#   See class Command



from Command import Command                     #   import parent class

class SmallTalk(Command):
    def __init__(this, name, kw = {}):          #   initialisation of new command
        super().__init__(name, kw)              #   call Command constructor

    def start(this, string):                    #   main method
        print('Im using smalltalk now :)')

    def confirm(this):                          #   optional method
        return true

    #   setters
    def setStart(this, function):               #   define start    (required)
        this.start = function

    def setConfirm(this, function):             #   define confirm (optional)
        this.confirm = function
