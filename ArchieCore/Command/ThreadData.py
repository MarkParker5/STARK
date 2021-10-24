from .RThread import RThread, Event

class ThreadData:
    thread: RThread
    finishEvent: Event

    def __init__(thread: RThread, finishEvent: Event):
        self.thread = thread
        self.finishEvent = finishEvent
