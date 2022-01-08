from typing import Optional, Any
from enum import Enum, auto
from .Command import Command
from .ThreadData import ThreadData

class ResponseAction(Enum):
    popContext = auto()
    popToRootContext = auto()
    sleep = auto()
    repeatLastAnswer = auto()
    commandNotFound = auto()
    answerNotFound = auto()

class Response:
    voice: str
    text: str
    context: list[Command]
    parameters: dict[str, Any]
    thread: Optional[ThreadData]
    actions: Optional[ResponseAction]
    data: dict[str, Any]

    def __init__(self, voice, text, context = [], parameters: dict[str, Any] = {}, thread = None, action = None, actions = []):
        self.voice = voice
        self.text = text
        self.context = context
        self.parameters = parameters
        self.thread = thread
        self.actions = actions
        self.actions.append(action)
