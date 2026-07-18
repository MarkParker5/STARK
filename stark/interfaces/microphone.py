from __future__ import annotations

from queue import Empty, Queue
from typing import Any, Callable

import anyio


class Microphone:
    def __init__(self, callback: Callable[[Any], None], device_id: int | None = None):
        try:
            from sounddevice import query_devices
        except ImportError:
            raise ImportError(
                "sounddevice is required for Microphone. Install it with: pip install stark-engine[sound]"
            )
        self.callback = callback
        self.device_id = device_id
        device_info = query_devices(device_id, kind="input") if device_id is not None else query_devices(kind="input")
        self.samplerate = int(device_info["default_samplerate"])
        self.blocksize = 8000
        self.dtype = "int16"
        self.channels = 1
        self.audio_queue: Queue = Queue()

    @staticmethod
    def list_devices() -> list[dict]:
        try:
            from sounddevice import query_devices
        except ImportError:
            raise ImportError(
                "sounddevice is required for Microphone. Install it with: pip install stark-engine[sound]"
            )
        devices = query_devices()
        return [
            {"id": i, "name": d["name"], "channels": d["max_input_channels"], "samplerate": d["default_samplerate"]}
            for i, d in enumerate(devices)
            if d["max_input_channels"] > 0
        ]

    async def start_listening(self):
        from sounddevice import RawInputStream

        with RawInputStream(
            device=self.device_id,
            samplerate=self.samplerate,
            blocksize=self.blocksize,
            dtype=self.dtype,
            channels=self.channels,
            callback=self._audio_input_callback,
        ):
            while True:
                try:
                    data = self.audio_queue.get_nowait()
                except Empty:
                    await anyio.sleep(0.01)
                    continue
                self.callback(data)

    def _audio_input_callback(self, indata, frames, time, status):
        self.audio_queue.put(bytes(indata))
