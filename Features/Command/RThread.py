from threading import Thread, Event

class RThread(Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._return = None

    def run(self):
        if self._target: self._return = self._target(*self._args, **self._kwargs)

    def join(self, *args, **kwargs):
        super().join(*args, **kwargs)
        return self._return
