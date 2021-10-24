from typing import Optional
from .Command import Command
from .ThreadData import ThreadData

class Response:
    voice: str
    text: str
    callback: Optional[Command]
    thread: Optional[ThreadData]

    def __init__(self, voice, text, callback = None, thread = None):
        self.voice = voice
        self.text = text
        self.callback = callback
        self.thread = thread
