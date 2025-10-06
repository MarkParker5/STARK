from dataclasses import dataclass
from itertools import groupby
from typing import Iterable, Optional

from stark.tools.levenshtein import levenshtein_similarity_substring
from stark.tools.phonetic.ipa import phonetic
from stark.tools.phonetic.simplephone import simplephone
from stark.tools.strtools import find_substring_in_words_map, split_indices

from .models import (
    DictionaryItem,
    DictionaryStorageProtocol,
    LookupResult,
    Metadata,
    Span,
)


@dataclass(frozen=True)
class NameEntry:
    language_code: str
    name: str
    metadata: Optional[Metadata] = None

class Dictionary:
    """
    Phonetic-aware dictionary with metadata storage.
    """

    def __init__(self, storage: DictionaryStorageProtocol):
        self.storage = storage

    # ----------------------
    # Write methods
    # ----------------------
    def write_one(self, language_code: str, name: str, metadata: Optional[Metadata] = None):
        """
        Add a single entry to the dictionary.
        Phonetic conversion happens internally (mandatory).
        """
        phonetic_str = phonetic(name, language_code=language_code)
        simple_phonetic = simplephone(phonetic_str) or ''
        item = DictionaryItem(
            name=name,
            phonetic=phonetic_str,
            simple_phonetic=simple_phonetic,
            metadata=metadata or {}
        )
        self.storage.write_one(item)

    def write_all(self, names: list[NameEntry]):
        """
        Add multiple entries in batch. Replaces existing entries.
        """
        self.clear()
        for entry in names:
            self.write_one(entry.language_code, entry.name, entry.metadata)

    def clear(self) -> None:
        """
        Clear all entries from the dictionary.
        """
        self.storage.clear()

    # ----------------------
    # Lookup methods
    # ----------------------
    def lookup(self, name_candidate: str, language_code: str, fast: bool = True) -> list[DictionaryItem]:
        """

        """
        simple_phonetic = simplephone(phonetic(name_candidate, language_code)) or ''
        matches = self.storage.search_equal_simple_phonetic(simple_phonetic)
        if not fast and not matches:
            matches = self.storage.search_contains_simple_phonetic(simple_phonetic)
        self._sort_matches(language_code, name_candidate, matches)
        # TODO: find a way to also return indices
        return matches

    def sentence_search(self, sentence: str, language_code: str) -> list[LookupResult]:

        # 1. build map like this: [
        # ...
        # ((4,7), 'bar', 'BR'),
        # ((5,11), 'baz', ''BZ),
        # ...
        # ]
        # 2. then use find_substring_in_words to:
        # 2.1. receive substr:str='BRBZ' and list list of BR, BZ, etc ~~words: list[tuple[indices, word, simplfied]]~~
        # 2.2 iterate over the list of simplified words, looking for single interceptions resulting in full match (containing) across neighboring words; return matched indexes
        # 2.3. combine matches of words list items into one (4,11), 'bar baz' (space joined), 'BRBZ' (just joined)

        # note: strings like 'foo bar baz test ber buz foo' will contain the match twice, so the final result must be
        # ((4,11), 'bar baz', 'BRBZ')
        # ((17,24), 'ber buz', 'BRBZ')

        @dataclass(frozen=True)
        class WordTrack:
            span: Span
            text: str
            simple_phonetic: str

        words_track_list = [
            WordTrack(
                span=Span(*indices),
                text=sentence[slice(*indices)],
                simple_phonetic=simplephone(phonetic(sentence[slice(*indices)], language_code)) or ''
            )
            for indices in split_indices(sentence)
        ]

        simple_sentence = ''.join(w.text for w in words_track_list)

        all_matches = self.storage.search_contains_simple_phonetic(simple_sentence)
        grouped_matches = groupby(all_matches, key=lambda x: x.simple_phonetic)

        if not all_matches:
            return []

        backtacked_matches: list[LookupResult] = []
        # for each matched simple code from the dictionary
        for simple_name, dictionary_matches in grouped_matches:
            # simple_name - simple code of a multiword name from dictionary

            # for each occurrence of the simple code in the sentence
            for words_indices in find_substring_in_words_map(simple_name, [w.simple_phonetic for w in words_track_list]):
                # combine spans per word into one multiword span
                subsentence_str = ' '.join(words_track_list[i].text for i in words_indices)
                span_start = words_track_list[words_indices[0]].span.start
                span_end = words_track_list[words_indices[-1]].span.end

                backtacked_matches.append(LookupResult(
                    Span(span_start, span_end),
                    self._sort_matches(language_code, subsentence_str, dictionary_matches)
                ))

        return backtacked_matches

    def _sort_matches(self, language_code: str, name_candidate: str, matches: Iterable[DictionaryItem]) -> list[DictionaryItem]:
        # sort by levenshtein distance of strings' latin representations
        return sorted(matches, key=lambda match: levenshtein_similarity_substring(phonetic(name_candidate, language_code), match.phonetic))

    # ----------------------
    # Optional / Advanced
    # ----------------------
    async def build(self) -> None:
        """
        Generate a static dictionary at build-time instead of runtime.
        """
        pass
