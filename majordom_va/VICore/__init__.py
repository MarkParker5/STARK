from .patterns import Pattern, expressions
from .VIObjects import (
    VIString,
    VIWord,
    # VINumber,
    # VITimeInterval
    # VITime,
)
from .CommandsFlow import (
    Command,
    Response,
    ResponseAction,
    CommandsManager,
    CommandsContext,
    CommandsContextDelegate
)


Pattern.argumentTypes = {
    'VIString': VIString,
    'VIWord': VIWord,
    # 'VINumber': VINumber,
    # 'VITimeInterval': VITimeInterval,
    # 'VITime': VITime,
}