from __future__ import annotations

import inspect
from dataclasses import dataclass
from types import UnionType

from stark.core.parsing import MatchResult

from .command import AsyncResponseHandler, Command, CommandRunner, ResponseHandler
from .patterns import Pattern


@dataclass
class SearchResult:
    command: Command
    match_result: MatchResult
    index: int = 0


class CommandsManager:
    name: str
    commands: list[Command]

    def __init__(self, name: str = ""):
        self.name = name or "CommandsManager"
        self.commands = []

    def get_by_name(self, name: str) -> Command | None:
        for command in self.commands:
            if command.name in {f"{self.name}.{name}", name}:
                return command
        return None

    def new(self, pattern_str: str, hidden: bool = False):
        def creator(runner: CommandRunner) -> Command:
            pattern = Pattern(pattern_str)

            # take the main type from Optionals
            annotations = dict()
            for param_name, param_type in runner.__annotations__.items():
                if isinstance(param_type, UnionType):
                    for sub_type in param_type.__args__:
                        if sub_type is not type(None):
                            annotations[param_name] = sub_type
                            break
                else:
                    annotations[param_name] = param_type

            # TODO: fix this after PatternParser refactoring
            # # check that runner has all parameters from pattern

            # error_msg = f"Command {self.name}.{runner.__name__} must have all parameters from pattern;"
            # pattern_params = set((p.name, Pattern._parameter_types[p.type_name].type.__name__) for p in pattern.parameters.values())
            # command_params = set(
            #     (
            #         k,
            #         get_args(v)[0].__name__ if type(None) in get_args(v) else v.__name__,
            #     )
            #     for k, v in annotations.items()
            # )
            # difference = pattern_params - command_params

            # # TODO: handle unregistered parameter type as a separate error

            # assert not difference, (
            #     error_msg + f"\n\tPattern got {dict(pattern_params)},\n\tFunction got {dict(command_params)},\n\tDifference: {dict(difference)}"
            # )
            # # assert {(p.name, p.type) for p in pattern.parameters.values()} <= annotations.items(), error_msg

            # additional checks for DI

            if ResponseHandler in runner.__annotations__.values() and inspect.iscoroutinefunction(runner):
                raise TypeError(
                    f"`ResponseHandler` is not compatible with command {self.name}.{runner.__name__} because it is async, use `AsyncResponseHandler` instead"
                )

            if AsyncResponseHandler in runner.__annotations__.values() and not inspect.iscoroutinefunction(runner):
                raise TypeError(
                    f"`AsyncResponseHandler` is not compatible with command {self.name}.{runner.__name__} because it is sync, use `ResponseHandler` instead"
                )

            # create command

            cmd = Command(f"{self.name}.{runner.__name__}", pattern, runner)

            if not hidden:
                self.commands.append(cmd)

            return cmd

        return creator

    def extend(self, other_manager: CommandsManager):
        self.commands.extend(other_manager.commands)
