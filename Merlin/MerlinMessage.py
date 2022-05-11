from typing import List

class MerlinMessage:
    urdi: bytes
    func: int # unsigned 1 byte int 0...255
    arg: int  # unsigned 1 byte int 0...255

    def __init__(self, urdi, func, arg):
        if type(urdi) == int:
            urdi = urdi.to_bytes(5, byteorder = 'big')
        self.urdi = urdi
        self.func = func
        self.arg = arg

    @property
    def data(self) -> List[int]:
        return [self.func, self.arg]
