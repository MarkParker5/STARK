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
    ResponseHandler,
    CommandsManager,
    CommandsContext,
    CommandsContextDelegate
)


Pattern.add_parameter_type(VIString)
Pattern.add_parameter_type(VIWord)