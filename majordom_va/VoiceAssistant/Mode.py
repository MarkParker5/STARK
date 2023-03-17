from __future__ import annotations
from typing import Callable
from pydantic import BaseModel
from general.classproperty import classproperty


class Mode(BaseModel):
    
    play_responses: bool = True
    collect_responses: bool = False
    needs_explicit_interaction: bool = False
    timeout_after_interaction: int = 20
    timeout_before_repeat: int = 5
    mode_on_timeout: Callable[[], Mode] | None = None
    mode_on_interaction: Callable[[], Mode] | None = None
    
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
    
    @classproperty
    def sleeping(cls) -> Mode:
        return Mode(
            play_responses = False,
            collect_responses = True,
            timeout_after_interaction = 0, # start collecting responses immediately
            timeout_before_repeat = 0, # repeat all
            needs_explicit_interaction = True,
            mode_on_interaction = lambda: Mode.active,
        )
    
    @classproperty
    def explicit(cls) -> Mode:
        return Mode(
            needs_explicit_interaction = True,
        )