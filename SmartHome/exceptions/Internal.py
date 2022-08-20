from enum import IntEnum


class ExceptionCode(IntEnum):
    undefined = 1000
    unauthorized = 1001
    access_denied = 1003
    not_found = 1004
    already_exist = 1005
    not_initialized = 1006
    invalid_format = 1022

class InternalException(Exception):
    Code = ExceptionCode

    def __init__(self, code: Code | int = Code.undefined, msg: str = '', debug: str = ''):
        self.code = code
        self.msg = msg
        self.debug = debug or msg
