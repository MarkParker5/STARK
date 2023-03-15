from __future__ import annotations
from typing import Type
from pydantic import BaseModel

from ..patterns import Pattern, MatchResult
from ..VIObjects import *
from .Threads import ThreadData, RThread, Event
from .Command import Command, CommandRunner, Response


class SearchResult(BaseModel):
    command: Command
    match_result: MatchResult = None
    index: int = 0
    
    class Config:
        arbitrary_types_allowed = True

class CommandsManager:
    
    name: str
    commands: list[Command]
    QA: Command = None
    
    def __init__(self, name: str = ''):
        self.name = name or 'CommandsManager'
        self.commands = []

    def search(self, string: str, commands: list[Command] = None) -> list[SearchResult]:
        
        if not commands:
            commands = self.commands
        
        results: list[SearchResult] = []
        origin = VIString(string)

        i = 0
        for command in commands:
            for match in command.pattern.match(string):
                results.append(SearchResult(
                    command = command,
                    match_result = match,
                    index = i
                ))
                i += 1
                
        # resolve overlapped results
        
        results = sorted(results, key = lambda result: result.match_result.start)
        
        for prev, current in zip(results.copy(), results[1:]): # copy to prevent affecting iteration by removing items; slice makes copy automatically
            if prev.match_result.start == current.match_result.start or prev.match_result.end > current.match_result.start:
                
                prev_cut = prev.command.pattern.match(string[prev.match_result.start:current.match_result.start]) # constrain prev end to current start
                current_cut = current.command.pattern.match(string[prev.match_result.end:current.match_result.end]) # constrain current start to prev end

                # less index = more priority to save full match
                priority1, priority2 = prev, current if prev.index < current.index else current, prev
                priority1_cut, priority2_cut = prev_cut, current_cut if prev.index < current.index else current_cut, prev_cut
                
                if new_matches := priority2_cut: # if can cut less priority
                    priority2.match_result = new_matches[0]
                elif new_matches := priority1_cut: # else if can cut more priority
                    priority1.match_result = new_matches[0]
                else: # else remove less priority
                    results.remove(priority2)
                
        # fallback to QA

        if not results and (qa := self.QA):
            results.append(SearchResult(
                command = qa,
                origin = origin
            ))

        return results
    
    def new(self, pattern_str: str, hidden: bool = False):
        def creator(func: CommandRunner) -> Command:
            pattern = Pattern(pattern_str)
            
            error_msg = f'Command {self.name}.{func.__name__} must have all parameters from pattern: {pattern.parameters=} {func.__annotations__=}'
            assert pattern.parameters.items() <= func.__annotations__.items(), error_msg
            
            cmd = Command(f'{self.name}.{func.__name__}', pattern, func)
            if not hidden:
                self.commands.append(cmd)
            
            return cmd
        return creator
    
    def extend(self, other_manager: CommandsManager):
        self.commands.extend(other_manager.commands)

    @staticmethod
    def background(first_response: Response):
        def decorator(origin_runner: CommandRunner):
            def sync_command_runner(*args, **kwargs):
                finish_event = Event()
                
                def background_command_runner():
                    response = origin_runner(*args, **kwargs) # can be long, blocking
                    finish_event.set()
                    return response
                
                thread = RThread(target=background_command_runner)
                thread.start()
                first_response.thread = ThreadData(thread = thread, finish_event = finish_event)
                return first_response
            
            sync_command_runner.__annotations__ = origin_runner.__annotations__
            sync_command_runner.__name__ = f'background<{origin_runner.__name__}>'

            return sync_command_runner
        return decorator
