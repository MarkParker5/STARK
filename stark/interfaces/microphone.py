from typing import Callable, Any
from queue import Queue, Empty
import anyio
from sounddevice import query_devices, RawInputStream, CallbackFlags, _buffer as buffer


class Microphone:
    
    def __init__(self, callback: Callable[[Any], None]):
        self.callback = callback
        self.samplerate = int(query_devices(kind = 'input')['default_samplerate'])
        self.blocksize = 8000
        self.dtype = 'int16'
        self.channels = 1
        self.audio_queue: Queue[buffer] = Queue()
        self.listening = True
    
    async def start_listening(self):
        with RawInputStream(
                samplerate = self.samplerate,
                blocksize = self.blocksize,
                dtype = self.dtype,
                channels = self.channels,
                callback = self._audio_input_callback
            ):
            while self.listening:
                await anyio.sleep(0.01)
                try:
                    if (data := self.audio_queue.get(block = False)):
                        self.callback(data)
                except Empty:
                    pass

    def _audio_input_callback(self, indata: buffer, frames: int, time: float, status: CallbackFlags):
        self.audio_queue.put(bytes(indata))
