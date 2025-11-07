from __future__ import annotations
from typing import override

from asyncer import SoonValue, create_task_group
from .commands_context_processor import CommandsContextProcessor, ParsedType
from .commands_context import CommandsContextLayer
from .commands_manager import SearchResult
from .patterns.pattern import MatchResult, ParameterMatch
from .command import Command
from .types import Object


class CommandsContextSearchProcessor(CommandsContextProcessor):
    async def search(
        self,
        string: str,
        commands: list[Command],
        parsed_types: list[ParsedType] = [],
    ) -> list[SearchResult]:
        objects_cache: dict[str, Object] = {}  # TODO: remove entirely
        results: list[SearchResult] = []
        futures: list[tuple[Command, SoonValue[list[MatchResult]]]] = []

        # run concurent commands match
        async with create_task_group() as group:
            for command in commands:
                futures.append(
                    (
                        command,
                        group.soonify(command.pattern.match)(
                            string,
                            objects_cache,
                            self._get_prefill(parsed_types, command),
                        ),
                    )
                )

        # read all finished matches
        i = 0
        for command, future in futures:
            for match in future.value:  # empty for most of commands (not matched)
                results.append(
                    SearchResult(command=command, match_result=match, index=i)
                )
                i += 1

        # resolve overlapped results

        results = sorted(results, key=lambda result: result.match_result.start)

        # copy to prevent affecting iteration by removing items; slice makes copy automatically
        for prev, current in zip(
            results.copy(), results[1:]
        ):  # TODO: concurrent; optimize using cache
            if (
                prev.match_result.start == current.match_result.start
                or prev.match_result.end > current.match_result.start
            ):
                # constrain prev end to current start
                prev_cut = await prev.command.pattern.match(
                    string[prev.match_result.start : current.match_result.start],
                    objects_cache,
                    self._get_prefill(parsed_types, prev.command),
                )
                # constrain current start to prev end
                current_cut = await current.command.pattern.match(
                    string[prev.match_result.end : current.match_result.end],
                    objects_cache,
                    self._get_prefill(parsed_types, current.command),
                )

                # less index = more priority to save full match
                priority1, priority2 = (
                    (prev, current) if prev.index < current.index else (current, prev)
                )
                priority1_cut, priority2_cut = (
                    (prev_cut, current_cut)
                    if prev.index < current.index
                    else (current_cut, prev_cut)
                )

                if new_matches := priority2_cut:  # if can cut less priority
                    priority2.match_result = new_matches[0]
                elif new_matches := priority1_cut:  # else if can cut more priority
                    priority1.match_result = new_matches[0]
                else:  # else remove less priority
                    results.remove(priority2)

        return results

    def _get_prefill(self, parsed_types: list[ParsedType], command: Command):
        return {
            p.name: p.parsed_substr
            for p in self._get_parsed_parameters(parsed_types, command)
        }

    def _get_parsed_parameters(self, parsed_types: list[ParsedType], command: Command):
        # put parsed types to corresponding command parameter keys
        param_type_to_key = {
            p.type_name: p.name for p in command.pattern.parameters.values()
        }
        return [
            ParameterMatch(
                parsed_obj=p.parsed_obj,
                parsed_substr=p.parsed_substr,
                name=param_type_to_key[type(p.parsed_obj).__name__],
            )
            for p in parsed_types
            if p.parsed_obj and type(p.parsed_obj).__name__ in param_type_to_key
        ]

    # Implement CommandsContextProcessor

    @override
    async def process_context(
        self,
        string: str,
        context: CommandsContextLayer,
        parsed_types: list[ParsedType],
    ) -> list[SearchResult]:
        return await self.search(string, context.commands, parsed_types)
