from __future__ import annotations

from typing import override

from asyncer import SoonValue, create_task_group

from stark.core.parsing import MatchResult, PatternParser, RecognizedEntity
from stark.general.feature_flags import FeatureFlag, get_flag
from stark.general.localisation import LocaleString

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

        # matrix cross-language matching on alternative tracks
        if get_flag(FeatureFlag.ENABLE_MULTILANG_MATRIX):
            from stark.models.transcription_string import TranscriptionString

            if isinstance(string, TranscriptionString) and string.alternative_texts:
                for alt_lang, alt_text in string.alternative_texts.items():
                    if alt_lang == language_code:
                        continue
                    tracks_to_match.append((alt_text, alt_lang))

        # match all tracks concurrently
        all_futures: list[SoonValue[list[SearchResult]]] = []
        async with create_task_group() as group:
            for track_string, track_lang in tracks_to_match:
                all_futures.append(
                    group.soonify(self._match_commands)(
                        track_string, track_lang, pattern_parser, commands, recognized_entities
                    )
                )

        results: list[SearchResult] = []
        for future in all_futures:
            results.extend(future.value)

        # deduplicate cross-track matches via string's overlap detection
        if len(tracks_to_match) > 1:
            results = self._deduplicate_cross_track(results, string)

        # resolve overlapped results

        results = sorted(results, key=lambda result: result.match_result.start)

        # copy to prevent affecting iteration by removing items; slice makes copy automatically
        for prev, current in zip(results.copy(), results[1:]):  # TODO: concurrent; optimize using cache
            if (
                prev.match_result.start == current.match_result.start
                or prev.match_result.end > current.match_result.start
            ):
                # constrain prev end to current start
                prev_cut = await pattern_parser.match(
                    prev.command.get_pattern(language_code),
                    string[prev.match_result.start : current.match_result.start],
                    recognized_entities,
                )
                # constrain current start to prev end
                current_cut = await pattern_parser.match(
                    current.command.get_pattern(language_code),
                    string[prev.match_result.end : current.match_result.end],
                    recognized_entities,
                )

                # less index = more priority to save full match
                priority1, priority2 = (prev, current) if prev.index < current.index else (current, prev)
                priority1_cut, priority2_cut = (
                    (prev_cut, current_cut) if prev.index < current.index else (current_cut, prev_cut)
                )

                if new_matches := priority2_cut:  # if can cut less priority
                    priority2.match_result = new_matches[0]
                elif new_matches := priority1_cut:  # else if can cut more priority
                    priority1.match_result = new_matches[0]
                else:  # else remove less priority
                    results.remove(priority2)

        return results

    async def _match_commands(
        self,
        string: str | LocaleString,
        language_code: str,
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

    @staticmethod
    def _deduplicate_cross_track(results: list[SearchResult], string: LocaleString) -> list[SearchResult]:
        if len(results) <= 1:
            return results

        deduplicated: list[SearchResult] = []
        for result in results:
            is_duplicate = False
            for existing in deduplicated:
                if result.command.name != existing.command.name:
                    continue
                overlapping = string.are_substrings_overlapping(
                    result.match_result.substring,
                    existing.match_result.substring,
                )
                if overlapping is None:
                    continue
                if overlapping:
                    if len(result.match_result.substring) > len(existing.match_result.substring):
                        deduplicated.remove(existing)
                        deduplicated.append(result)
                    is_duplicate = True
                    break
            if not is_duplicate:
                deduplicated.append(result)
        return deduplicated

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
