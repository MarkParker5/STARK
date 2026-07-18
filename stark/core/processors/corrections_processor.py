from __future__ import annotations

import logging
from typing import TYPE_CHECKING, override

from stark.core.commands_context_processor import CommandsContextProcessor
from stark.core.commands_manager import SearchResult
from stark.core.parsing import RecognizedEntity
from stark.general.localisation import LocaleString

from ..commands_context import CommandsContext

if TYPE_CHECKING:
    from stark.tools.dictionary.dictionary import Dictionary, LookupMode

logger = logging.getLogger(__name__)


class CorrectionsProcessor(CommandsContextProcessor):
    """Pre-processor that generates phonetic corrections from dictionary lookups.

    Accepts any Dictionary instance(s) — including one built from recognizable.strings
    via build_recognizable_dictionary(). For each input word/phrase, runs dictionary
    sentence search and appends matching corrections to TranscriptionString.corrections.
    These are used by PatternParser._expand_corrections to widen compiled regexes.

    For multilingual input with alternative tracks, runs dictionary search per track
    and stores per-track corrections.

    Place this processor before SearchProcessor in the pipeline.
    """

    def __init__(
        self,
        dictionaries: list[Dictionary] | None = None,
        mode: LookupMode | None = None,
    ):
        self._dictionaries = dictionaries or []
        if mode is None:
            from stark.tools.dictionary.dictionary import LookupMode
            mode = LookupMode.AUTO
        self._mode = mode

    @override
    async def process_string(
        self,
        string: LocaleString,
        context: CommandsContext,
        recognized_entities: list[RecognizedEntity],
    ) -> tuple[list[SearchResult], int]:
        if not self._dictionaries:
            return [], 0

        from stark.models.transcription_string import TranscriptionString
        from stark.models.transcription_string import Correction

        if not isinstance(string, TranscriptionString):
            return [], 0

        self._find_corrections(str(string), string.language_code, string.corrections)

        if string.alternative_texts:
            for alt_lang, alt_text in string.alternative_texts.items():
                if alt_lang == string.language_code:
                    continue
                corrections: list[Correction] = []
                self._find_corrections(str(alt_text), alt_lang, corrections)
                if corrections:
                    string._corrections_by_track[alt_lang] = corrections

        return [], 0

    def _find_corrections(self, text: str, language_code: str, output: list):
        from stark.models.transcription_string import Correction

        for dictionary in self._dictionaries:
            for result in dictionary.search_in_sentence(text, language_code, self._mode):
                variant = text[result.span.slice]
                keyword = result.item.name
                if variant != keyword:
                    output.append(Correction(variant=variant, keyword=keyword))
