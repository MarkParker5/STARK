from typing import Protocol


class IpaProvider(Protocol):
    def to_ipa(self, string: str, language_code: str) -> str: ...
