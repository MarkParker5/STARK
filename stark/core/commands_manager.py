from __future__ import annotations
from dataclasses import dataclass
import inspect
from asyncer import create_task_group, SoonValue
import json

from .patterns import Pattern, MatchResult
from .types import Object
from .command import Command, CommandRunner, ResponseHandler, AsyncResponseHandler
from ..models.transcription import Transcription
from ..general.localisation import Localizer


@dataclass
class SearchResult:
    command: Command
    match_result: MatchResult
    index: int = 0

class CommandsManager:
    
    name: str
    commands: list[Command]
    
    def __init__(self, name: str = ''):
        self.name = name or 'CommandsManager'
        self.commands = []
        
    def get_by_name(self, name: str) -> Command | None:
        for command in self.commands:
            if command.name in {f'{self.name}.{name}', name}:
                return command
        return None
    
    def prepare(self, localizer: Localizer):
        for command in self.commands:
            command.pattern.prepare(localizer)

    async def search(self, transcription: Transcription, localizer: Localizer, commands: list[Command] | None = None) -> list[SearchResult]:
        
        if not commands:
            commands = self.commands
        
        objects_cache: dict[str, Object] = {}
        results: list[SearchResult] = []
        futures: list[tuple[Command, SoonValue[list[MatchResult]]]] = []
        
        # run concurent commands match 
        async with create_task_group() as group:
            for command in commands:
                futures.append((command, group.soonify(command.pattern.match)(transcription, localizer, objects_cache)))
        
        # read all finished matches
        i = 0
        for command, future in futures:
            for match in future.value: # may be empty for most of commands
                results.append(SearchResult(
                    command = command,
                    match_result = match,
                    index = i
                ))
                i += 1
        
        # resolve overlapped results
        
        results = sorted(results, key = lambda result: result.match_result.start)
        
        # copy to prevent affecting iteration by removing items; slice makes copy automatically
        for prev, current in zip(results.copy(), results[1:]):
            if prev.match_result.start == current.match_result.start or prev.match_result.end > current.match_result.start:
                
                # constrain prev end to current start
                prev_slice = transcription.get_slice(prev.match_result.start, current.match_result.start)
                prev_slice_match = await prev.command.pattern.match(prev_slice, localizer, objects_cache) 
                
                # constrain current start to prev end
                current_slice = transcription.get_slice(prev.match_result.end, current.match_result.end)
                current_slice_match = await current.command.pattern.match(current_slice, localizer, objects_cache)

                # less index = more priority to save full match
                priority1, priority2 = (prev, current) if prev.index < current.index else (current, prev)
                priority1_slice_match, priority2_slice_match = (prev_slice_match, current_slice_match) if prev.index < current.index else (current_slice_match, prev_slice_match)
                
                if new_matches := priority2_slice_match: # if can cut less priority
                    priority2.match_result = new_matches[0]
                elif new_matches := priority1_slice_match: # else if can cut more priority
                    priority1.match_result = new_matches[0]
                else: # else remove less priority
                    results.remove(priority2)
        
        print('results:', [result.command.name for result in results])
        return results 
    
    def new(self, pattern_str: str, hidden: bool = False):
        def creator(runner: CommandRunner) -> Command:
            pattern = Pattern(pattern_str)
            
            # check that runner has all parameters from pattern
            
            error_msg = f'Command {self.name}.{runner.__name__} must have all parameters from pattern: {pattern.parameters=} {runner.__annotations__=}'
            assert pattern.parameters.items() <= runner.__annotations__.items(), error_msg
            
            # additional checks for DI
            
            if ResponseHandler in runner.__annotations__.values() and inspect.iscoroutinefunction(runner):
                raise TypeError(f'`ResponseHandler` is not compatible with command {self.name}.{runner.__name__} because it is async, use `AsyncResponseHandler` instead')
            
            if AsyncResponseHandler in runner.__annotations__.values() and not inspect.iscoroutinefunction(runner):
                raise TypeError(f'`AsyncResponseHandler` is not compatible with command {self.name}.{runner.__name__} because it is sync, use `ResponseHandler` instead')
            
            # create command
            
            cmd = Command(f'{self.name}.{runner.__name__}', pattern, runner)
            
            if not hidden:
                self.commands.append(cmd)
            
            return cmd
        return creator
    
    def extend(self, other_manager: CommandsManager):
        self.commands.extend(other_manager.commands)
