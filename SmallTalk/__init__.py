#   Initialisation SmallTalk
#   Creating objects (add commands)
#   setStart(method) is required
#   setConfirm(method) is optional
#
#   How to add new command:
#   1.  def method()                 #  return string
#   1.2 def confirm_method()         #  optional, not required
#   2.  kw = {
#           (int)weight  : ['word1', 'word2', 'word3'],
#           (int)weight1 : ['word3', 'word4'],
#           (int)weight2 : ['word5', 'word6', 'word7', 'word8', 'word9'],
#       }
#       patterns = ['* который * час *', '* скольк* * (врем|час)* *']
#       subpatterns = [...]     #like patterns
#   3.  new_command = SmallTalk(Name, kw, patterns, subpatterns)
#   4.  new_command.setStart(method)
#   5.  new_command.setConfirm(confirm_method)    # optional, not required
#
#   @background(voice_to_speak, text_for_print) for background methods

from .hello import *
from .ctime import *
from .test import *
