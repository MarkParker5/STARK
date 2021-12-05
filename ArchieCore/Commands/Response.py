from typing import Optional, Any
from enum import Enum, auto
from .Command import Command
from .ThreadData import ThreadData

class ResponseAction(Enum):
    popContext = auto()
    popToRootContext = auto()
    sleep = auto()
    repeatLastAnswer = auto()
    answerNotFound = auto()

class Response:
    voice: str
    text: str
    context: list[Command]
    thread: Optional[ThreadData]
    action: Optional[ResponseAction]
    data: dict[str, Any]

    def __init__(self, voice, text, context = [], thread = None, action = None):
        self.voice = voice
        self.text = text
        self.context = context
        self.thread = thread
        self.action = action
