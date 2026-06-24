from __future__ import annotations

import logging
from typing import override

from stark.core.commands_context_processor import CommandsContextProcessor
from stark.core.commands_manager import SearchResult
from stark.core.parsing import RecognizedEntity
from stark.general.localisation import LocaleString

from ..commands_context import CommandsContext

logger = logging.getLogger(__name__)


class RecognizableAlternativesProcessor(CommandsContextProcessor):
    """Pre-processor that generates phonetic alternatives from recognizable strings.

    Reads recognizable strings from the Localizer, computes phonetic suggestions
    against the input text, and appends them to TranscriptionString.recognizable_alternatives.
    These are used by PatternParser._expand_recognizable_suggestions to widen
    compiled regexes — automatically enabled when alternatives are present.

    Place this processor before SearchProcessor in the pipeline.

    Complexity: O(R * W) where R = number of recognizable strings in the active language,
    W = number of words in input. Each comparison is a levenshtein_similarity call which
    is O(len(candidate) * len(keyword)) — typically short strings (1-3 words).
    Memory: O(S) where S = number of suggestions generated (typically small).
    """

    @override
    async def process_string(
        self,
        string: LocaleString,
        context: CommandsContext,
        recognized_entities: list[RecognizedEntity],
    ) -> tuple[list[SearchResult], int]:
        from stark.models.transcription_string import TranscriptionString

        localizer = context.pattern_parser.localizer
        if not localizer or not isinstance(string, TranscriptionString):
            return [], 0

        try:
            from stark.tools.levenshtein import levenshtein_similarity
        except ImportError:
            logger.warning("levenshtein not available, skipping recognizable alternatives")
            return [], 0

        language_code = string.language_code
        recognizable = localizer.recognizable.get(language_code) or localizer.recognizable.get("base")
        if not recognizable:
            return [], 0

        input_words = str(string).split()

        for string_entry in recognizable.strings.values():
            keyword = string_entry.value
            keyword_words = keyword.split()
            if not keyword_words:
                continue

            # slide keyword-length window over input words
            for i in range(len(input_words) - len(keyword_words) + 1):
                candidate = " ".join(input_words[i : i + len(keyword_words)])
                if candidate == keyword:
                    continue
                sim = levenshtein_similarity(s1=candidate, s2=keyword)
                if sim > 0.6:
                    from stark.models.voice_transcription import Suggestion

                    string.recognizable_alternatives.append(Suggestion(variant=candidate, keyword=keyword))

        return [], 0
