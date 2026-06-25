from __future__ import annotations

from typing import override

from asyncer import SoonValue, create_task_group

from stark.core.parsing import MatchResult, PatternParser, RecognizedEntity
from stark.general.feature_flags import FeatureFlag, get_flag
from stark.general.localisation import LocaleString
from stark.general.localisation.language_code import LanguageCode

from ..command import Command
from ..commands_context import CommandsContext, CommandsContextLayer
from ..commands_context_processor import CommandsContextProcessor
from ..commands_manager import SearchResult


class SearchProcessor(CommandsContextProcessor):
    async def search(
        self,
        string: str | LocaleString,
        pattern_parser: PatternParser,
        commands: list[Command],
        recognized_entities: list[RecognizedEntity],
    ) -> list[SearchResult]:
        string = string if isinstance(string, LocaleString) else LocaleString(string)
        language_code = string.language_code

        # collect all tracks to match (primary + alternatives)
        tracks_to_match: list[tuple[str | LocaleString, str]] = [(string, language_code)]

        if get_flag(FeatureFlag.ENABLE_MULTILANG_MATRIX):
            from stark.models.transcription_string import TranscriptionString

            if isinstance(string, TranscriptionString) and string.alternative_texts:
                for alt_lang, alt_text in string.alternative_texts.items():
                    if alt_lang == language_code:
                        continue
                    tracks_to_match.append((alt_text, alt_lang))

        # match all tracks concurrently, tag results with source text and language
        all_futures: list[tuple[str, str, SoonValue[list[SearchResult]]]] = []
        async with create_task_group() as group:
            for track_string, track_lang in tracks_to_match:
                all_futures.append(
                    (
                        str(track_string),
                        track_lang,
                        group.soonify(self._match_commands)(
                            track_string, track_lang, pattern_parser, commands, recognized_entities
                        ),
                    )
                )

        tagged: list[tuple[str, str, SearchResult]] = []
        global_index = 0
        for source_text, track_lang, future in all_futures:
            for r in future.value:
                r.index = global_index
                global_index += 1
                tagged.append((source_text, track_lang, r))

        # sort by start position (translated to primary track for ordering)
        # primary = str(string)
        # tagged.sort(key=lambda t: string.translate_position(t[2].match_result.start, t[0], primary))
        tagged.sort(key=lambda t: t[2].match_result.start)

        # resolve overlaps — each result lives in its own source track's coordinates
        # translate between tracks on demand for comparison and cutting
        for prev_entry, current_entry in zip(tagged.copy(), tagged[1:]):
            prev_src, prev_lang, prev = prev_entry
            current_src, current_lang, current = current_entry

            # check for overlaps
            try:
                current_start_in_prev = string.translate_position(current.match_result.start, current_src, prev_src)
            except ValueError:
                # can't translate between tracks — drop lower priority
                loser_entry = current_entry if prev.index < current.index else prev_entry
                if loser_entry in tagged:
                    tagged.remove(loser_entry)
                continue

            if current_start_in_prev is None or prev.match_result.end <= current_start_in_prev:
                # no overlap
                continue

            # overlap — try to cut each in its own source text
            try:
                prev_end_in_current = string.translate_position(prev.match_result.end, prev_src, current_src)
            except ValueError:
                loser_entry = current_entry if prev.index < current.index else prev_entry
                if loser_entry in tagged:
                    tagged.remove(loser_entry)
                continue

            prev_cut = (
                await pattern_parser.match(
                    prev.command.get_pattern(prev_lang),
                    prev_src[prev.match_result.start : current_start_in_prev],
                    recognized_entities,
                )
                if current_start_in_prev > prev.match_result.start
                else []
            )

            current_cut = (
                await pattern_parser.match(
                    current.command.get_pattern(current_lang),
                    current_src[prev_end_in_current : current.match_result.end],
                    recognized_entities,
                )
                if prev_end_in_current is not None and prev_end_in_current < current.match_result.end
                else []
            )

            # less index = more priority to save full match
            is_prev_priority = prev.index < current.index
            loser_cut = current_cut if is_prev_priority else prev_cut
            winner_cut = prev_cut if is_prev_priority else current_cut
            loser_entry = current_entry if is_prev_priority else prev_entry
            winner_entry = prev_entry if is_prev_priority else current_entry

            if new_matches := loser_cut:
                loser_entry[2].match_result = new_matches[0]
            elif new_matches := winner_cut:
                winner_entry[2].match_result = new_matches[0]
            else:
                if loser_entry in tagged:
                    tagged.remove(loser_entry)

        return [r for _, _, r in tagged]

    async def _match_commands(
        self,
        string: str | LocaleString,
        language_code: LanguageCode,
        pattern_parser: PatternParser,
        commands: list[Command],
        recognized_entities: list[RecognizedEntity],
    ) -> list[SearchResult]:
        results: list[SearchResult] = []
        futures: list[tuple[Command, SoonValue[list[MatchResult]]]] = []

        # run concurent commands match
        async with create_task_group() as group:
            for command in commands:
                futures.append(
                    (
                        command,
                        group.soonify(pattern_parser.match)(
                            command.get_pattern(language_code), string, recognized_entities
                        ),
                    )
                )

        # read all finished matches
        i = 0
        for command, future in futures:
            for match in future.value:  # empty for most of commands (not matched)
                results.append(SearchResult(command=command, match_result=match, index=i))
                i += 1

        return results

    # Implement CommandsContextProcessor

    @override
    async def process_context_layer(
        self,
        string: LocaleString,
        context: CommandsContext,
        context_layer: CommandsContextLayer,
        recognized_entities: list[RecognizedEntity],
    ) -> list[SearchResult]:
        return await self.search(string, context.pattern_parser, context_layer.commands, recognized_entities)
