from typing import override
from stark.core.patterns import ParseError, Pattern
from stark.core.types import Object
from stark.general.classproperty import classproperty

from .dictionary import Dictionary, LookupMode
from .models import LookupResult


class NLDictionaryName(Object[list[LookupResult]]):
    value: list[LookupResult]
    dictionary: Dictionary

    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern("**")

    @override
    async def did_parse(self, from_string: str):
        lang = "en"
        self.value = list(
            self.dictionary.search_in_sentence(from_string, lang, mode=LookupMode.AUTO)
        )  # TODO: consider using lookup method
        if len(self.value) == 0:
            raise ParseError(f"Could not find '{from_string}' in dictionary")
        if len(self.value) == 1:
            return from_string[self.value[0].span.slice]
        else:
            # TODO: review getting substring with multiple matches
            min_start = min(match.span.start for match in self.value)
            max_end = max(match.span.end for match in self.value)
            return from_string[min_start:max_end]
