from pydantic import BaseModel
from .RThread import RThread, Event


class ThreadData(BaseModel):
    thread: RThread
    finishEvent: Event