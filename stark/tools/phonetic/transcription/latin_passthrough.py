from __future__ import annotations

from stark.general.localisation.language_code import LanguageCode
from stark.tools.phonetic.transcription.protocol import IpaProvider


class LatinPassthroughProvider:
    """IPA provider that skips transcription for latin-only text.

    Returns the input lowercased if all characters are latin letters or spaces.
    Delegates to a fallback provider for non-latin text. Raises ValueError if
    non-latin text is encountered with no fallback configured.
    """

    def __init__(self, fallback: IpaProvider | None = None):
        self._fallback = fallback

    def to_ipa(self, string: str, language_code: LanguageCode) -> str:
        if all(c.isascii() and (c.isalpha() or c.isspace()) for c in string):
            return string.lower()
        if self._fallback:
            return self._fallback.to_ipa(string, language_code)
        raise ValueError(
            f"Non-latin text '{string}' requires a fallback IPA provider"
        )
