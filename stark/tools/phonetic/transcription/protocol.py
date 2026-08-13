from typing import Hashable, Protocol

from stark.general.localisation.language_code import LanguageCode


class IpaProvider(Hashable, Protocol):
    def to_ipa(self, string: str, language_code: LanguageCode) -> str: ...
