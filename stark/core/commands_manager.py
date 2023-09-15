from __future__ import annotations
from dataclasses import dataclass
import inspect
import asyncer

from .patterns import Pattern, MatchResult
from .types import Object
from .command import Command, CommandRunner


@dataclass
class SearchResult:
    command: Command
    match_result: MatchResult
    index: int = 0

class CommandsManager:
    
    name: str
    commands: list[Command]
    QA: Command | None = None
    
    def __init__(self, name: str = ''):
        self.name = name or 'CommandsManager'
        self.commands = []

    def search(self, string: str, commands: list[Command] | None = None) -> list[SearchResult]:
        
        if not commands:
            commands = self.commands
        
        objects_cache: dict[str, Object] = {}
        results: list[SearchResult] = []
        # origin = String(string)

        i = 0
        for command in commands:
            for match in command.pattern.match(string, objects_cache):
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
                prev_cut = prev.command.pattern.match(string[prev.match_result.start:current.match_result.start], objects_cache) 
                # constrain current start to prev end
                current_cut = current.command.pattern.match(string[prev.match_result.end:current.match_result.end], objects_cache)

                # less index = more priority to save full match
                priority1, priority2 = (prev, current) if prev.index < current.index else (current, prev)
                priority1_cut, priority2_cut = (prev_cut, current_cut) if prev.index < current.index else (current_cut, prev_cut)
                
                if new_matches := priority2_cut: # if can cut less priority
                    priority2.match_result = new_matches[0]
                elif new_matches := priority1_cut: # else if can cut more priority
                    priority1.match_result = new_matches[0]
                else: # else remove less priority
                    results.remove(priority2)
                
        return results 
    
    def new(self, pattern_str: str, hidden: bool = False):
        def creator(runner: CommandRunner) -> Command:
            pattern = Pattern(pattern_str)
            
            error_msg = f'Command {self.name}.{runner.__name__} must have all parameters from pattern: {pattern.parameters=} {runner.__annotations__=}'
            assert pattern.parameters.items() <= runner.__annotations__.items(), error_msg
            
            if not inspect.iscoroutinefunction(runner):
                async_runner = asyncer.asyncify(runner) # type: ignore
                async_runner.__name__ = runner.__name__
                async_runner.__annotations__ = runner.__annotations__
            else:
                async_runner = runner
            
            cmd = Command(f'{self.name}.{runner.__name__}', pattern, async_runner) # type: ignore
            
            if not hidden:
                self.commands.append(cmd)
            
            return cmd
        return creator
    
    def extend(self, other_manager: CommandsManager):
        self.commands.extend(other_manager.commands)