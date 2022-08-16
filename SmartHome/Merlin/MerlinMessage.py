from typing import List

class MerlinMessage:
    urdi: int
    func: int # unsigned 1 byte int 0...255
    arg: int  # unsigned 1 byte int 0...255

    def __init__(self, urdi, func, arg):
        self.urdi = urdi
        self.func = func
        self.arg = arg

    @property
    def data(self) -> List[int]:
        return [self.func, self.arg]
