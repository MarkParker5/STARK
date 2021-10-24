import time
import requests
import json as JSON

from ..Control import Control
from ArchieCore import Command
from Features import *

class RemoteControl(Control):
    url = 'http://t97316v1.beget.tech/read'
    session = requests.Session()

    def start(self):
        while True:
            time.sleep(1)
            strings = self.session.get(self.url, headers = {'User-Agent': 'Mozilla/5.0'}).text.split('<br>')
            if not strings: continue

            for string in strings:
                try: data = JSON.loads(string)
                except: continue
                if name := data.get('cmd'):
                    if cmd := Command.getCommand(name):
                        params = data.get('params') or {}
                        try: cmd.start(params)
                        except: pass
