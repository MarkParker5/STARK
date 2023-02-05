from typing import Optional, Any
from enum import Enum, auto
from pydantic import BaseModel
from .Command import Command
from .ThreadData import ThreadData


class ResponseAction(Enum):
    popContext = auto()
    popToRootContext = auto()
    sleep = auto()
    repeatLastAnswer = auto()
    commandNotFound = auto()
    answerNotFound = auto()

class Response(BaseModel):
    voice: str
    text: str
    context: list[Command]
    parameters: dict[str, Any]
    thread: Optional[ThreadData]
    actions: Optional[ResponseAction]
    # data: dict[str, Any]
