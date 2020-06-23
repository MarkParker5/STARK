#   File for test modules
#   Program work only here
#   :)
from Command import Command
import SmallTalk
import Text2Speech

archie = Text2Speech.Engine()

archie.generate('Привет', True)
Text2Speech.Speech.getList()[0].speak()

while True:
    string = str(input('-> '))
    archie.generate( Command.find(string).start() ).speak()
