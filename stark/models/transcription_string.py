from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from stark.general.localisation.language_code import LanguageCode
from stark.general.localisation.locale_string import LocaleString


@dataclass(frozen=True)
class TranscriptionWord:
    word: str
    language_code: LanguageCode
    char_start: int
    char_end: int


class TranscriptionString(LocaleString):
    """A LocaleString with per-word language metadata and optional alternative tracks.

    Each word carries its own ``language_code``, allowing the parsing pipeline
    to resolve the correct language for each parameter substring. The overall
    ``language_code`` property returns the majority language of the word list.

    Alternative texts (``_alternative_texts``) carry the same utterance as
    transcribed by different language models. The parser can iterate over them
    for cross-language matrix matching.
    """

    _words: tuple[TranscriptionWord, ...]
    _alternative_texts: dict[str, LocaleString]
    recognizable_alternatives: list
    _language_code_override: LanguageCode | None

    def __new__(
        cls,
        value: str = "",
        language_code: LanguageCode | None = None,
        words: tuple[TranscriptionWord, ...] | list[TranscriptionWord] = (),
        alternative_texts: dict[str, LocaleString] | None = None,
        recognizable_alternatives: list | None = None,
    ) -> TranscriptionString:
        resolved_words = tuple(words)
        resolved_lang = language_code or _majority_language(resolved_words) or "base"
        instance = super().__new__(cls, value, resolved_lang)
        instance._words = resolved_words
        instance._alternative_texts = alternative_texts or {}
        instance.recognizable_alternatives = list(recognizable_alternatives or [])
        instance._language_code_override = language_code
        return instance

    @classmethod
    def from_words(
        cls,
        words: list[tuple[str, LanguageCode]],
        alternative_texts: dict[str, LocaleString] | None = None,
        recognizable_alternatives: list | None = None,
    ) -> TranscriptionString:
        text_parts: list[str] = []
        tw_list: list[TranscriptionWord] = []
        offset = 0
        for word, lang in words:
            char_start = offset
            char_end = offset + len(word)
            tw_list.append(TranscriptionWord(word, lang, char_start, char_end))
            text_parts.append(word)
            offset = char_end + 1  # +1 for space
        text = " ".join(text_parts)
        return cls(
            text,
            words=tw_list,
            alternative_texts=alternative_texts,
            recognizable_alternatives=recognizable_alternatives,
        )

    @property
    def language_code(self) -> LanguageCode:
        if self._words:
            return _majority_language(self._words) or "base"
        return self._language_code_override or "base"

    @language_code.setter
    def language_code(self, value: LanguageCode):
        self._language_code_override = value

    @property
    def words(self) -> tuple[TranscriptionWord, ...]:
        return self._words

    @property
    def alternative_texts(self) -> dict[str, LocaleString]:
        return self._alternative_texts

    # --- core overrides ---

    def _with(self, value: str) -> TranscriptionString:
        try:
            start = str.index(self, value)
        except ValueError:
            return TranscriptionString(
                value, self.language_code, (), self._alternative_texts, self.recognizable_alternatives
            )
        end = start + len(value)
        return self._slice_by_offset(value, start, end)

    def __getitem__(self, key) -> TranscriptionString:
        result_str = str.__getitem__(self, key)
        if isinstance(key, slice):
            start = key.start or 0
            if start < 0:
                start = max(0, len(self) + start)
            end = start + len(result_str)
            return self._slice_by_offset(result_str, start, end)
        else:
            idx = key if key >= 0 else len(self) + key
            return self._slice_by_offset(result_str, idx, idx + 1)

    def replace(self, old: str, new: str, count: int = -1) -> TranscriptionString:
        result_text = str.replace(self, old, new, count)
        try:
            old_start = str.index(self, old)
        except ValueError:
            return TranscriptionString(result_text, self.language_code, self._words, self._alternative_texts)

        old_end = old_start + len(old)
        len_diff = len(new) - len(old)

        new_words: list[TranscriptionWord] = []
        for w in self._words:
            if w.char_start >= old_start and w.char_end <= old_end:
                if new:
                    new_words.append(TranscriptionWord(new, w.language_code, old_start, old_start + len(new)))
                    new = ""  # only add replacement word once
                continue
            if w.char_start >= old_end:
                new_words.append(
                    TranscriptionWord(w.word, w.language_code, w.char_start + len_diff, w.char_end + len_diff)
                )
            else:
                new_words.append(w)

        return TranscriptionString(
            result_text, None, new_words, self._alternative_texts, self.recognizable_alternatives
        )

    def strip(self, chars: str | None = None) -> TranscriptionString:
        result_str = str.strip(self, chars)
        if not result_str:
            return TranscriptionString(
                "", self.language_code, (), self._alternative_texts, self.recognizable_alternatives
            )
        start = str.index(self, result_str)
        end = start + len(result_str)
        return self._slice_by_offset(result_str, start, end)

    def split(self, sep: str | None = None, maxsplit: int = -1) -> list[TranscriptionString]:
        parts = str.split(self, sep, maxsplit)
        result: list[TranscriptionString] = []
        search_start = 0
        for part in parts:
            if not part:
                result.append(
                    TranscriptionString(
                        "", self.language_code, (), self._alternative_texts, self.recognizable_alternatives
                    )
                )
                continue
            try:
                idx = str.index(self, part, search_start)
            except ValueError:
                result.append(TranscriptionString(part, self.language_code, (), self._alternative_texts))
                continue
            result.append(self._slice_by_offset(part, idx, idx + len(part)))
            search_start = idx + len(part)
        return result

    # --- internal ---

    def _slice_by_offset(self, value: str, start: int, end: int) -> TranscriptionString:
        filtered = tuple(
            TranscriptionWord(w.word, w.language_code, w.char_start - start, w.char_end - start)
            for w in self._words
            if w.char_start >= start and w.char_end <= end
        )
        return TranscriptionString(value, None, filtered, self._alternative_texts, self.recognizable_alternatives)

    # translate_position: inherited from LocaleString (identity).
    # Cross-track overlap resolution requires timestamps — use VoiceTranscriptionString.

    def __repr__(self) -> str:
        return (
            f"TranscriptionString({str.__repr__(self)}, language_code={self.language_code!r}, words={len(self._words)})"
        )


def _majority_language(words: tuple[TranscriptionWord, ...] | list[TranscriptionWord]) -> LanguageCode | None:
    if not words:
        return None
    counts = Counter(w.language_code for w in words)
    return counts.most_common(1)[0][0]
