import time
import anyio


class BlockageDetector:
    def __init__(self, threshold = 1.0):
        self._threshold = threshold
        self._last_update = time.monotonic()
        self._running = True

    async def monitor(self):
        self._last_update = time.monotonic()
        self._running = True
        while self._running:
            current_time = time.monotonic()
            gap = current_time - self._last_update
            if gap > self._threshold:
                self.handle_blockage(gap)
            self._last_update = current_time
            await anyio.sleep(self._threshold / 4)

    def handle_blockage(self, gap: float):
        print(f'[RuntimeWarning] Main thread was blocked for {gap:.1f}s!')

    def stop(self):
        self._running = False
