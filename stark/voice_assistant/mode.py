from __future__ import annotations
from typing import Optional, Callable
from pydantic import BaseModel
from ..general.classproperty import classproperty


class Mode(BaseModel):
    
    play_responses: bool = True
    collect_responses: bool = False
    explicit_interaction_pattern: Optional[str] = None
    timeout_after_interaction: int = 20 # seconds
    timeout_before_repeat: int = 5 # seconds
    mode_on_timeout: Callable[[], Mode] | None = None
    mode_on_interaction: Callable[[], Mode] | None = None
    stop_after_interaction: bool = False
    
    @classproperty
    def active(cls) -> Mode:
        return Mode(
            mode_on_timeout = lambda: Mode.waiting,
        )
    
    @classproperty
    def waiting(cls) -> Mode:
        return Mode(
            collect_responses = True,
            mode_on_interaction = lambda: Mode.active,
        )
    
    @classproperty
    def inactive(cls) -> Mode:
        return Mode(
            play_responses = False,
            collect_responses = True,
            timeout_after_interaction = 0, # start collecting responses immediately
            timeout_before_repeat = 0, # repeat all
            mode_on_interaction = lambda: Mode.active,
        )
    
    @classmethod
    def sleeping(cls, pattern: str) -> Mode:
        return Mode(
            play_responses = False,
            collect_responses = True,
            timeout_after_interaction = 0, # start collecting responses immediately
            timeout_before_repeat = 0, # repeat all
            explicit_interaction_pattern = pattern,
            mode_on_interaction = lambda: Mode.active,
        )
    
    @classmethod
    def explicit(cls, pattern: str) -> Mode:
        return Mode(
            explicit_interaction_pattern = pattern,
        )
        
    @classmethod
    def external(cls) -> Mode:
        return Mode(
            stop_after_interaction = True,
        )
