from typing import Callable, Any
from VICore import VITime, VITimeInterval
from .. import Identifable, threadingFunction

class DispatchQueueItem(Identifable):
    time: VITime
    timeinterval: VITimeInterval
    worker: Callable
    args: list[Any]
    kwargs: dict[Any, Any]
    repeat: bool

    def __init__(self, execute: Callable, time: VITime = VITime(), timeinterval: VITimeInterval = VITimeInterval(0),
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
