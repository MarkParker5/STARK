from typing import Callable, Optional
from time import sleep

from ArchieCore.ACObjects import ACTime, ACTimeInterval
from .. import Singleton, UUID, threadingFunction
from .DispatchQueueItem import DispatchQueueItem

class DispatchQueue(Singleton):
    _queue: [DispatchQueueItem] = []
    _nearestItemTime: Optional[ACTime] = None

    def asyncAt(self, time: ACTime, execute: Callable, *args, **kwargs) -> UUID:
        item = DispatchQueueItem(execute = execute, time = time, args = args, kwargs = kwargs)
        self.insert(item)
        return item.id

    def asyncAfter(self, timeinterval: ACTimeInterval, execute: Callable, *args, **kwargs) -> UUID:
        time = ACTime().addingInterval(timeinterval)
        item = DispatchQueueItem(execute = execute, time = time, timeinterval = timeinterval,
                                 args = args, kwargs = kwargs)
        self.insert(item)
        return item.id

    def repeatEvery(self, timeinterval: ACTimeInterval, execute: Callable, *args, **kwargs) -> UUID:
        time = ACTime().addingInterval(timeinterval)
        item = DispatchQueueItem(execute = execute, time = time, timeinterval = timeinterval,
                                 repeat = True, args = args, kwargs = kwargs)
        self.insert(item)
        return item.id

    def insert(self, item: DispatchQueueItem):
        now = ACTime()
        low = 0
        high = len(self._queue)

        while low < high:
            mid = (low + high) // 1
            if self._queue[mid].time < now: low = mid + 1
            else: high = mid

        self._queue.insert(low, item)
        self._nearestItemTime = self._queue[0].time

    def invalidate(self, id: UUID) -> DispatchQueueItem:
        for i, item in enumerate(self._queue):
            if item.id != id: continue
            if i == 0: self._nearestItemTime = self._queue[1].time if len(self._queue) > 1 else None
            return self._queue.pop(i)

    @threadingFunction
    def loop(self):
        while True:

            if not self._queue or not self._nearestItemTime or self._nearestItemTime > ACTime():
                sleep(0.1)
                continue

            item = self._queue.pop(0)
            item.execute()

            if item.repeat:
                item.time.addInterval(item.timeinterval)
                self.insert(item)

            self._nearestItemTime = self._queue[0].time if self._queue else None

DispatchQueue().loop()
