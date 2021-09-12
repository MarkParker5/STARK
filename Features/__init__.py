from .Command import Command
from .Command import Response

from .Media import Media
from .QA.QA import QA
from .SmallTalk import SmallTalk
from .Raspi import Raspi
from .Zieit import Zieit

try: from .SmartHome import SmartHome
except: print('cannot import module named "SmartHome" from Features/Smarthome\n')
