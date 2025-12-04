from __future__ import annotations

from typing import override

from asyncer import SoonValue, create_task_group

from stark.core.parsing import MatchResult, PatternParser, RecognizedEntity

from ..command import Command
from ..commands_context import CommandsContext, CommandsContextLayer
from ..commands_context_processor import CommandsContextProcessor
from ..commands_manager import SearchResult


class SearchProcessor(CommandsContextProcessor):
    async def search(
        self,
        string: str,
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
                        group.soonify(pattern_parser.match)(command.pattern, string, recognized_entities),
                    )
                )

        # read all finished matches
        i = 0
        for command, future in futures:
            for match in future.value:  # empty for most of commands (not matched)
                results.append(SearchResult(command=command, match_result=match, index=i))
                i += 1

        # resolve overlapped results

        results = sorted(results, key=lambda result: result.match_result.start)

        # copy to prevent affecting iteration by removing items; slice makes copy automatically
        for prev, current in zip(results.copy(), results[1:]):  # TODO: concurrent; optimize using cache
            if prev.match_result.start == current.match_result.start or prev.match_result.end > current.match_result.start:
                # constrain prev end to current start
                prev_cut = await pattern_parser.match(
                    prev.command.pattern, string[prev.match_result.start : current.match_result.start], recognized_entities
                )
                # constrain current start to prev end
                current_cut = await pattern_parser.match(
                    current.command.pattern, string[prev.match_result.end : current.match_result.end], recognized_entities
                )

                # less index = more priority to save full match
                priority1, priority2 = (prev, current) if prev.index < current.index else (current, prev)
                priority1_cut, priority2_cut = (prev_cut, current_cut) if prev.index < current.index else (current_cut, prev_cut)

                if new_matches := priority2_cut:  # if can cut less priority
                    priority2.match_result = new_matches[0]
                elif new_matches := priority1_cut:  # else if can cut more priority
                    priority1.match_result = new_matches[0]
                else:  # else remove less priority
                    results.remove(priority2)

        return results

    # Implement CommandsContextProcessor

    @override
    async def process_context_layer(
        self,
        string: str,
        context: CommandsContext,
        context_layer: CommandsContextLayer,
        recognized_entities: list[RecognizedEntity],
    ) -> list[SearchResult]:
        return await self.search(string, context.pattern_parser, context_layer.commands, recognized_entities)
