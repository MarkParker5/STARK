import time
import anyio


class BlockageDetector:
    def __init__(self, threshold = 1.0):
        self._threshold = threshold
        self._last_update = time.time()
        self._running = True

    async def monitor(self):
        self._running = True
        while self._running:
            current_time = time.time()
            if current_time - self._last_update > self._threshold:
                self.handle_blockage()
            self._last_update = current_time
            await anyio.sleep(self._threshold / 4)

    def handle_blockage(self):
        print(f'[RuntimeWarning] Main thread was blocked for more than {self._threshold}s!')

    def stop(self):
        self._running = False
