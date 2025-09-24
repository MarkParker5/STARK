from stark.core.patterns import ParseError, Pattern
from stark.core.types import Object
from stark.general.classproperty import classproperty

from .dictionary import Dictionary
from .models import DictionaryItem


class NLDictionaryName(Object):
    value: list[DictionaryItem]
    dictionary: Dictionary

    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern('**')

    async def did_parse(self, from_string: str):
        if not (matches := self.dictionary.lookup(from_string)):
            raise ParseError(f"Could not find '{from_string}' in dictionary")
        self.value = matches
        return from_string
