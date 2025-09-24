from itertools import groupby
from typing import Any, Dict, Iterable, Optional

from stark.tools.levenshtein import levenshtein_similarity
from stark.tools.phonetic.ipa import phonetic
from stark.tools.phonetic.simplephone import simplephone
from stark.tools.strtools import find_substring_in_words_map, split_indices

from .models import DictionaryItem, DictionaryStorageProtocol, Metadata

# TODO: dataclasses instead of tuples

class Dictionary:
    """
    Phonetic-aware dictionary with metadata storage.
    """

    def __init__(self, storage: DictionaryStorageProtocol):
        self.storage = storage
        self._data: Dict[str, Dict[str, Any]] = {}  # id -> {simplephone, origin, metadata}

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

    def write_all(self, names: list[tuple[str, str, Optional[Metadata]]]):
        """
        Add multiple entries in batch. Replaces existing entries.
        """
        self.clear()
        for language_code, name, metadata in names:
            self.write_one(language_code, name, metadata)

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

    def sentence_search(self, sentence: str, language_code: str) -> list[DictionaryItem]:

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

        words_track_list = [
            (
                indices,
                sentence[slice(*indices)],
                simplephone(phonetic(sentence[slice(*indices)], language_code)) or ''
            )
            for indices in split_indices(sentence)
        ]

        simple_sentence = ''.join(word for _, word, _ in words_track_list)

        all_matches = self.storage.search_contains_simple_phonetic(simple_sentence)
        grouped_matches = groupby(all_matches, key=lambda x: x.simple_phonetic)

        if not all_matches:
            return []

        backtacked_matches = []
        # for each matched simple code from the dictionary
        for simple_name, dictionary_matches in grouped_matches:
            # simple_name - simple code of a multiword name from dictionary

            # for each occurrence of the simple code in the sentence
            for words_indices in find_substring_in_words_map(simple_name, [w[2] for w in words_track_list]):
                # combine indices per word into one multiword indices tuple
                subsentence_str = ' '.join(words_track_list[i][1] for i in words_indices)
                # subsentence_simple = ''.join(words_track_list[i][2] for i in words_indices)
                subsentence_indices = (words_track_list[words_indices[0]][0], words_track_list[words_indices[-1]][0])

                backtacked_matches.append((subsentence_indices, self._sort_matches(language_code, subsentence_str, dictionary_matches)))

        return backtacked_matches

    def _sort_matches(self, language_code: str, name_candidate: str, matches: Iterable[DictionaryItem]) -> list[DictionaryItem]:
        # sort by levenshtein distance of strings' latin representations
        return sorted(matches, key=lambda match: levenshtein_similarity(phonetic(name_candidate, language_code), match.phonetic))

    # ----------------------
    # Optional / Advanced
    # ----------------------
    async def build(self) -> None:
        """
        Generate a static dictionary at build-time instead of runtime.
        """
        pass
