#   Initialisation SmallTalk
#   Creating objects (add commands)
#   setStart(method) is required
#   setConfirm(method) is optional
#
#   How to add new command:
#   1.  def method()
#   1.2 def confirm_method()         # optional, not required
#   2.  kw = {
#           (int)weight  : ['word1', 'word2', 'word3'],
#           (int)weight1 : ['word3', 'word4'],
#           (int)weight2 : ['word5', 'word6', 'word7', 'word8', 'word9'],
#       }
#   3.  new_command = SmallTalk(Name, kw)
#   4.  new_command.setStart(method)
#   5.  new_command.setConfirm(confirm_method)    # optional, not required



from .SmallTalk import *

################################################################################
def method(string):
    print('Hello')
kw = {
    1: ['Lorem', 'ipsum', 'dolor'],
    2: ['Lorem2', 'ipsum2', 'dolor2'],
}
hello = SmallTalk('First', kw)
hello.setStart(method)
################################################################################
