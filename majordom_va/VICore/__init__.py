from .patterns import Pattern, expressions
from .VIObjects import (
    VIString,
    VIWord,
    VINumber,
    VITime,
    VITimeInterval
)
# from .Commands import (
    
# )


Pattern.argumentTypes = {
    'VIString': VIString,
    'VIWord': VIWord,
    'VINumber': VINumber,
    'VITime': VITime,
    'VITimeInterval': VITimeInterval,
}