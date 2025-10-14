from stark.core.patterns import ParseError, Pattern
from stark.core.types import Object
from stark.general.classproperty import classproperty

from .dictionary import Dictionary
from .models import DictionaryItem


class NLDictionaryName(Object[DictionaryItem]):
    # value: list[DictionaryItem]
    value: DictionaryItem
    dictionary: Dictionary

    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern('**')

    async def did_parse(self, from_string: str):
        lang = "en"
        if not (matches := self.dictionary.sentence_search_sorted(from_string, lang)):
        # if not (matches := self.dictionary.lookup_sorted(from_string, lang)):
            raise ParseError(f"Could not find '{from_string}' in dictionary")
        match = matches[0]
        self.value = match.item
        return from_string[match.span.slice]
