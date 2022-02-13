class MerlinMessage:
    urdi: int # unsigned 4 bytes (32bit) int 0...2^32
    func: int # unsigned 1 byte int 0...255
    arg: int  # unsigned 1 byte int 0...255

    leadingMarker = ord('<')
    trailingMarker = ord('>')

    def __init__(self, urdi, func, arg):
        self.urdi = urdi
        self.func = func
        self.arg = arg

    @classmethod
    def parseRaw(cls, rawData: bytearray) -> 'MerlinMessage':
        if len(rawData) < 8:
            return None
        if rawData[0] != cls.leadingMarker or rawData[-1] != cls.trailingMarker:
            return None

        urdi = int.from_bytes(rawData[1:5], byteorder = 'big')
        func = int(rawData[5])
        arg = int(rawData[6])

        return cls(urdi, func, arg)

    @property
    def rawData(self) -> bytearray:
        msg = bytearray(8)
        msg[0] = self.leadingMarker
        msg[1] = (self.urdi >> 24) & 0xFF
        msg[2] = (self.urdi >> 16) & 0xFF
        msg[3] = (self.urdi >> 8) & 0xFF
        msg[4] = self.urdi & 0xFF
        msg[5] = self.func;
        msg[6] = self.arg;
        msg[7] = self.trailingMarker
        return msg
