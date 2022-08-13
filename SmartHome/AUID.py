from typing import NamedTuple
from enum import Enum, auto
from uuid import UUID
import time
import qrcode
from qrcode.image.pil import PilImage


__all__ = ['UUID',]

class URDI(int):
    def __repr__(self) -> str:
        return f'URDI({super().__repr__()})'

class Model(int, Enum):
    zero = 0
    hub = 1
    relay = 2

class Version(tuple[int, int], Enum):
    zero = (0, 0)
    dev = (0, 1)
    test = (0, 2)
    prod = (1, 1)

class UUIDItems(NamedTuple):
    time: int
    time_low: int
    model: Model
    version: Version
    urdi: URDI

class AUID(UUID):

    @classmethod
    def new(cls, model: Model = None, version: Version = None, urdi: int = None, now=time.time()) -> 'UUID':
        now = now or 0
        model = model or Model.zero
        version = version or Version.zero
        urdi = urdi or 0
        now = now or 0

        time = int(now)
        time_low = int((now % 1) * 255 * 2)

        return cls(fields=(time, time_low, model.value, *version.value, urdi))

    @property
    def items(self) -> UUIDItems:
        time, time_low, model, *ver, urdi = self.fields
        return UUIDItems(time, time_low, Model(model), Version(tuple(ver)), URDI(urdi))

    @property
    def qrcode(self) -> PilImage:
        return qrcode.make(str(self))
