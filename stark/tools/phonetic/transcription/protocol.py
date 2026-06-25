from typing import Protocol

from stark.general.localisation.language_code import LanguageCode


class IpaProvider(Protocol):
    def to_ipa(self, string: str, language_code: LanguageCode) -> str: ...
