from .patterns import Pattern, expressions
from .VIObjects import (
    VIObject,
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


Pattern.add_parameter_type(VIString)
Pattern.add_parameter_type(VIWord)