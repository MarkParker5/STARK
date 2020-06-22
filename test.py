#   File for test modules
#   Program work only here
#   :)
from Command import Command
import SmallTalk
import Text2Speech

archie = Text2Speech.engine()

while True:
    string = str(input('-> '))
    archie.generate( Command.find(string).start() ).speak()
