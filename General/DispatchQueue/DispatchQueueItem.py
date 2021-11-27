from typing import Callable, Any
from ArchieCore import ACTime, ACTimeInterval
from .. import Identifable, threadingFunction

class DispatchQueueItem(Identifable):
    time: ACTime
    timeinterval: ACTimeInterval
    worker: Callable
    args: list[Any]
    kwargs: dict[Any, Any]
    repeat: bool

    def __init__(self, execute: Callable, time: ACTime = ACTime(), timeinterval: ACTimeInterval = ACTimeInterval(0),
                 repeat: bool = False, args: list[Any] = [], kwargs: dict[Any, Any] = []):
        self.time = time
        self.timeinterval = timeinterval
        self.worker = execute
        self.args = args
        self.kwargs = kwargs
        self.repeat = repeat

    @threadingFunction
    def execute(self):
        self.worker(*self.args, **self.kwargs)
