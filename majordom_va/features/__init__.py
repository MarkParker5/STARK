from VICore import CommandsManager
from . import smalltalk


default = CommandsManager('default')
default.extend(smalltalk.manager)