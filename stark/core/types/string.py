from .object import NLObject


class NLString(NLObject):
    """
    Space separated alphanumerics words.
    """

    value: str
