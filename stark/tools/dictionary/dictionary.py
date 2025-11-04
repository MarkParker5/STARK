import logging
from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum, auto
from itertools import groupby
from typing import final

from stark.tools.common.span import Span
from stark.tools.levenshtein import (
    SIMPLEPHONE_PROXIMITY_GRAPH,
    SKIP_SPACES_GRAPH,
    levenshtein_match,
    levenshtein_search_substring,
    levenshtein_similarity,
    levenshtein_similarity_substring,
)
from stark.tools.phonetic.transcription import (
    transcription,
    IpaProvider,
    EspeakIpaProvider,
)
from stark.tools.phonetic.simplephone import simplephone
from stark.tools.strtools import find_substring_in_words_map, split_indices

from .models import (
    DictionaryItem,
    DictionaryStorageProtocol,
    LookupResult,
    Metadata,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class NameEntry:
    language_code: str
    name: str
    metadata: Metadata | None = None


class LookupMode(Enum):
    EXACT = auto()  # the fastest
    CONTAINS = auto()  # fast
    FUZZY = auto()  # slow
    AUTO = auto()  # choose the best mode based on the dictionary size


class LookupField(Enum):
    NAME = auto()  # search by original name, same lang only
    PHONETIC = auto()  # search by simplephone cross-lang


class Dictionary:
    """
    Phonetic-aware dictionary with metadata storage.
    """

    def __init__(
        self,
        storage: DictionaryStorageProtocol,
        ipa_provider: IpaProvider = EspeakIpaProvider(),
    ):
        self.storage: DictionaryStorageProtocol = storage
        self.ipa_provider: IpaProvider = ipa_provider

    # ----------------------
    # Write methods
    # ----------------------
    def write_one(
        self, language_code: str, name: str, metadata: Metadata | None = None
    ):  # TODO: overload to accept NameEntry
        """
        Add a single entry to the dictionary.
        Phonetic conversion happens internally (mandatory).
        """
        phonetic_str = transcription(
            name, language_code=language_code, ipa_provider=self.ipa_provider
        )
        simple_phonetic = simplephone(phonetic_str) or ""
        item = DictionaryItem(
            name=name,
            phonetic=phonetic_str,
            simple_phonetic=simple_phonetic,
            language_code=language_code,
            metadata=metadata or {},
        )
        self.storage.write_one(item)
        logger.debug(
            f"Written entry '{name}' with phonetic '{phonetic_str}' and simple phonetic '{simple_phonetic}'"
        )

    def write_all(self, names: list[NameEntry]):
        """
        Add multiple entries in batch. Replaces existing entries.
        """
        self.clear()
        for entry in names:
            self.write_one(entry.language_code, entry.name, entry.metadata)

    def clear(self):
        """
        Clear all entries from the dictionary.
        """
        self.storage.clear()

    # ----------------------
    # Lookup methods
    # ----------------------

    def lookup_sorted(
        self,
        name_candidate: str,
        language_code: str,
        mode: LookupMode = LookupMode.AUTO,
        field: LookupField = LookupField.PHONETIC,
    ) -> list[DictionaryItem]:
        return self._sorted_items(
            language_code,
            name_candidate,
            self.lookup(name_candidate, language_code, mode, field),
        )

    def search_in_sentence_sorted(
        self,
        sentence: str,
        language_code: str,
        mode: LookupMode = LookupMode.EXACT,
        field: LookupField = LookupField.PHONETIC,
    ) -> list[LookupResult]:
        return sorted(
            self.search_in_sentence(sentence, language_code, mode, field),
            key=lambda r: levenshtein_similarity_substring(
                s1=r.item.name
                if r.item.language_code == language_code
                else r.item.phonetic,
                s2=sentence
                if r.item.language_code == language_code
                else transcription(
                    sentence, language_code, ipa_provider=self.ipa_provider
                ),
                ignore_prefix=True,
            )[0][1],  # TODO: review
            reverse=True,
        )

    def lookup(
        self,
        name_candidate: str,
        language_code: str,
        mode: LookupMode = LookupMode.AUTO,
        field: LookupField = LookupField.PHONETIC,
    ) -> Iterable[DictionaryItem]:
        """
        Lookup dictionary items by name_candidate and language_code using LookupMode and LookupField.
        """
        simple_phonetic = (
            simplephone(
                transcription(
                    name_candidate, language_code, ipa_provider=self.ipa_provider
                )
            )
            or ""
        )
        logger.debug(
            f"Looking up '{name_candidate}' with simple phonetic '{simple_phonetic}' under mode {mode}, field {field}"
        )

        match mode:
            case LookupMode.EXACT:
                if field == LookupField.PHONETIC:
                    yield from self.storage.search_equal_simple_phonetic(
                        simple_phonetic
                    )
                elif field == LookupField.NAME:
                    yield from self.storage.search_equal_name(
                        name_candidate, language_code
                    )
            case LookupMode.CONTAINS:
                if field == LookupField.PHONETIC:
                    yield from self.storage.search_contains_simple_phonetic(
                        simple_phonetic
                    )
                elif field == LookupField.NAME:
                    yield from self.storage.search_contains_name(
                        name_candidate, language_code
                    )
            case LookupMode.FUZZY:
                if field == LookupField.PHONETIC:
                    yield from filter(
                        lambda item: levenshtein_match(
                            s1=item.simple_phonetic,
                            s2=simplephone(
                                transcription(
                                    name_candidate,
                                    language_code,
                                    ipa_provider=self.ipa_provider,
                                )
                            )
                            or "",
                            threshold=0.8,
                            proximity_graph=SIMPLEPHONE_PROXIMITY_GRAPH,
                        ),
                        self.storage.iterate(),
                    )
                elif field == LookupField.NAME:
                    yield from (
                        item
                        for item in self.storage.search_contains_name(
                            name_candidate, language_code
                        )
                        if levenshtein_match(
                            s1=item.name,
                            s2=name_candidate,
                            threshold=0.8,
                            proximity_graph=SIMPLEPHONE_PROXIMITY_GRAPH,
                        )
                    )
            case LookupMode.AUTO:
                search_orders = (
                    [  # TODO: Consider inverting the order and filtering to min threshold to improve performance of both success and failure cases
                        (LookupField.NAME, LookupMode.EXACT),
                        (LookupField.NAME, LookupMode.CONTAINS),
                        (LookupField.PHONETIC, LookupMode.EXACT),
                        (LookupField.PHONETIC, LookupMode.CONTAINS),
                        (LookupField.PHONETIC, LookupMode.FUZZY),
                    ]
                    if field == LookupField.PHONETIC
                    else [
                        (field, LookupMode.EXACT),
                        (field, LookupMode.CONTAINS),
                        (field, LookupMode.FUZZY),
                    ]
                )
                for f, m in search_orders:
                    if m == LookupMode.FUZZY and self.storage.get_count() > 10**3:
                        continue
                    gen = iter(self.lookup(name_candidate, language_code, m, f))
                    try:
                        first: DictionaryItem = next(gen)
                    except StopIteration:
                        continue
                    else:
                        yield first
                        yield from gen
                        break

    def search_in_sentence(
        self,
        sentence: str,
        language_code: str,
        mode: LookupMode = LookupMode.AUTO,
        field: LookupField = LookupField.PHONETIC,
    ) -> Iterable[LookupResult]:
        """
        Sentence search supporting LookupField and LookupMode, matching lookup logic.
        """
        logger.debug(
            f"Sentence search '{sentence}' with lang '{language_code}', mode {mode}, field {field}"
        )

        match mode:
            case LookupMode.EXACT | LookupMode.CONTAINS:
                if field == LookupField.PHONETIC:
                    yield from self._search_in_sentence_per_word(
                        sentence, language_code, mode
                    )
                elif field == LookupField.NAME:
                    items = self.storage.search_contains_name(sentence, language_code)
                    for item in items:
                        start = 0
                        while True:  # find all occurrences
                            idx = sentence.find(item.name, start)
                            if idx == -1:
                                break
                            span = Span(idx, idx + len(item.name))
                            yield LookupResult(span, item)
                            start = idx + 1
            case LookupMode.FUZZY:
                if field == LookupField.PHONETIC:
                    simple_phonetic = (
                        simplephone(
                            transcription(
                                sentence, language_code, ipa_provider=self.ipa_provider
                            )
                        )
                        or ""
                    )
                    for item in self.storage.iterate():
                        for span, _ in levenshtein_search_substring(
                            s1=simple_phonetic,
                            s2=item.simple_phonetic,
                            ignore_prefix=True,
                            threshold=0.8,
                            proximity_graph=SIMPLEPHONE_PROXIMITY_GRAPH,
                        ):
                            yield LookupResult(span, item)
                elif field == LookupField.NAME:
                    for item in self.storage.iterate():
                        for span, x in levenshtein_search_substring(
                            s1=sentence,
                            s2=item.name,
                            ignore_prefix=True,
                            threshold=0.8,
                            proximity_graph=SKIP_SPACES_GRAPH,
                        ):
                            yield LookupResult(span, item)
            case LookupMode.AUTO:
                search_orders = (
                    [
                        # (LookupField.NAME, LookupMode.EXACT),
                        (LookupField.NAME, LookupMode.CONTAINS),
                        (LookupField.PHONETIC, LookupMode.EXACT),
                        (LookupField.PHONETIC, LookupMode.CONTAINS),
                        (LookupField.PHONETIC, LookupMode.FUZZY),
                    ]
                    if field == LookupField.PHONETIC
                    else [
                        (field, LookupMode.EXACT),
                        (field, LookupMode.CONTAINS),
                        (field, LookupMode.FUZZY),
                    ]
                )
                for f, m in search_orders:
                    if m == LookupMode.FUZZY and self.storage.get_count() > 10**3:
                        continue
                    gen = iter(self.search_in_sentence(sentence, language_code, m, f))
                    try:
                        first: LookupResult = next(gen)
                    except StopIteration:
                        continue
                    else:
                        yield first
                        yield from gen
                        break

    def _search_in_sentence_per_word(
        self, sentence: str, language_code: str, mode: LookupMode = LookupMode.EXACT
    ) -> Iterable[LookupResult]:
        import logging

        logger = logging.getLogger(__name__)
        logger.debug(
            f"Sentence: '{sentence}' | Language: {language_code} | Mode: {mode}"
        )

        # 1. build map like this: [
        # ...
        # ((4,7), 'bar', 'BR'),
        # ((5,11), 'baz', ''BZ),
        # ...
        # ]
        # 2. then use find_substring_in_words to:
        # 2.1. receive substr:str='BRBZ' and list list of BR, BZ, etc ~~words: list[tuple[indices, word, simplfied]]~~
        # 2.2 iterate over the list of simplified words, looking for single interceptions resulting in full match (containing) across neighboring words; return matched indexes
        # 2.3. combine matches of words list items into one (4,11), 'bar baz' (space join), 'BRBZ' (zerowidth join)

        # note: strings like 'foo bar baz test ber buz foo' will contain the match twice, so the final result must be corresponding

        # return results
        # ((4,11), 'bar baz', 'BRBZ')
        # ((17,24), 'ber buz', 'BRBZ')

        # UPD: Alternative approach to consider: dynamic sliding window which expands the window only when there are candidates (startswith is true). Might be more efficient than the current approach.

        @dataclass(frozen=True)
        class WordTrack:
            span: Span
            text: str
            simple_phonetic: str

        words_track_list = [
            WordTrack(
                span=span,
                text=sentence[span.slice],
                simple_phonetic=simplephone(
                    transcription(
                        sentence[span.slice],
                        language_code,
                        ipa_provider=self.ipa_provider,
                    )
                )
                or "",
            )
            for span in split_indices(sentence)
        ]

        simple_sentence = " ".join(w.simple_phonetic for w in words_track_list)

        all_matches = self.storage.search_contains_simple_phonetic(simple_sentence)
        logger.debug(f"All multi-word matches: {[m.name for m in all_matches]}")
        grouped_matches = groupby(all_matches, key=lambda x: x.simple_phonetic)

        if not all_matches:
            return []

        # backtacked_matches: list[LookupResult] = []
        # for each matched simple code from the dictionary
        for simple_name, dictionary_matches in grouped_matches:
            # simple_name - simple code of a multiword name from dictionary

            # for each occurrence of the simple code in the sentence
            for words_indices in find_substring_in_words_map(
                simple_name, [w.simple_phonetic for w in words_track_list]
            ):
                # combine spans per word into one multiword span
                # subsentence_str = " ".join(
                #     words_track_list[i].text for i in words_indices
                # )
                span_start = words_track_list[words_indices[0]].span.start
                span_end = words_track_list[words_indices[-1]].span.end

                # backtacked_matches.append(LookupResult(
                #     Span(span_start, span_end),
                #     self._sorted_matches(language_code, subsentence_str, dictionary_matches)
                # ))

                for item in dictionary_matches:
                    yield LookupResult(Span(span_start, span_end), item)

                    # backtacked_matches.append(LookupResult(
                    #     Span(span_start, span_end),
                    #     item
                    # ))

        # return backtacked_matches

    def _sorted_items(
        self, language_code: str, name_candidate: str, matches: Iterable[DictionaryItem]
    ) -> list[DictionaryItem]:
        # sort by levenshtein distance of strings' latin representations

        matches = list(matches)

        if len(matches) < 2:
            return matches

        return sorted(
            matches,
            key=lambda item: levenshtein_similarity(
                s1=name_candidate
                if item.language_code == language_code
                else transcription(
                    name_candidate, language_code, ipa_provider=self.ipa_provider
                ),
                s2=item.name if item.language_code == language_code else item.phonetic,
            ),
            reverse=True,
        )

    # ----------------------
    # Optional / Advanced
    # ----------------------
    async def build(self):
        """
        Generate a static dictionary at build-time instead of runtime.
        """
        raise NotImplementedError("Dictionary.build() is not implemented")

    @final
    async def build_if_needed(self):
        """
        Calls build() if the storage is empty.
        """
        if self.storage.get_count() == 0:
            await self.build()
