from __future__ import annotations

import inspect
import logging
import warnings
from datetime import datetime
from enum import Enum, auto
from functools import update_wrapper, wraps
from typing import (
    Any,
    AsyncGenerator,
    Awaitable,
    Callable,
    ClassVar,
    Generator,
    Generic,
    Optional,
    Protocol,
    TypeVar,
    cast,
)
from uuid import UUID, uuid4

from typing_extensions import get_args

logger = logging.getLogger(__name__)

import asyncer
from pydantic import BaseModel, Field

from ..general.classproperty import classproperty
from ..general.localisation import LanguageCode, LocalizableString
from .patterns import Pattern

ResponseOptions = (
    Optional["Response"] | Generator[Optional["Response"], None, None] | AsyncGenerator[Optional["Response"], None]
)
AwaitResponse = Awaitable[ResponseOptions]
AsyncCommandRunner = Callable[..., AwaitResponse]
SyncCommandRunner = Callable[..., Optional["Response"]]
CommandRunner = TypeVar("CommandRunner", bound=SyncCommandRunner | AsyncCommandRunner)


class Command(Generic[CommandRunner]):
    name: str
    patterns: dict[LanguageCode, Pattern]
    _runner: CommandRunner

    def __init__(self, name: str, patterns: dict[LanguageCode, Pattern], runner: CommandRunner):
        assert patterns and all(isinstance(p, Pattern) for p in patterns.values())
        self.name = name
        self.patterns = patterns
        self._runner = runner
        update_wrapper(self, runner)

    def get_pattern(self, language_code: LanguageCode) -> Pattern:
        if language_code in self.patterns:
            return self.patterns[language_code]
        return self.patterns["base"]

    def run(
        self,
        parameters_dict: dict[str, Any] | None = None,
        /,
        **kwparameters: dict[str, Any],
    ) -> AwaitResponse:
        # allow call both with and without dict unpacking
        # e.g. command.run(foo = bar, lorem = ipsum), command.run(**parameters) and command.run(parameters)
        # where parameters is dict {'foo': bar, 'lorem': ipsum}

        parameters = parameters_dict or {}
        parameters.update(kwparameters)

        # auto fill optionals
        for param_name, param_type in self._runner.__annotations__.items():
            if param_name not in parameters and type(None) in get_args(param_type):
                parameters[param_name] = None

        runner: AsyncCommandRunner

        if inspect.iscoroutinefunction(self._runner) or inspect.isasyncgen(self._runner):
            # async functions (coroutines) and async generators are remain as is
            runner = cast(AsyncCommandRunner, self._runner)
        else:
            # sync functions are wrapped with asyncer.asyncify to make them async (coroutines)
            # async generators are not supported yet by asyncer.asyncify (https://github.com/tiangolo/asyncer/discussions/86)
            runner = asyncer.asyncify(cast(SyncCommandRunner, self._runner))

        if any(p.kind == p.VAR_KEYWORD for p in inspect.signature(self._runner).parameters.values()):
            # if command runner accepts **kwargs, pass all parameters
            coroutine = runner(**parameters)
        else:
            # otherwise pass only parameters that are in command runner signature to prevent TypeError: got an unexpected keyword argument
            coroutine = runner(**{k: v for k, v in parameters.items() if k in self._runner.__code__.co_varnames})

        @wraps(runner)
        async def coroutine_wrapper() -> ResponseOptions:
            try:
                response = await coroutine
            except Exception as e:
                logger.error(e)
                response = Response(
                    text=f"Command {self} raised an exception: {e.__class__.__name__}",
                    voice=f"Command {self} raised an exception: {e.__class__.__name__}",
                    status=ResponseStatus.error,
                )
            if inspect.isgenerator(response):
                message = (
                    f"[WARNING] Command {self} is a sync GeneratorType that is not fully supported and may block the main thread. "
                    + "Consider using the ResponseHandler.respond() or async approach instead."
                )
                warnings.warn(message, UserWarning)
            return response

        return coroutine_wrapper()

    def __call__(self, *args, **kwargs) -> AwaitResponse:
        # just syntactic sugar for command(...) instead of command.run(...)
        return self.run(*args, **kwargs)

    def __repr__(self):
        return f"<Command {self.name}>"


class ResponseStatus(Enum):
    none = auto()
    not_found = auto()
    failed = auto()
    success = auto()
    info = auto()
    error = auto()


class Response(BaseModel):
    voice: str | LocalizableString = ""
    text: str | LocalizableString = ""
    status: ResponseStatus = ResponseStatus.success
    needs_user_input: bool = False
    commands: list[Command] = []
    parameters: dict[str, Any] = {}

    id: UUID = Field(default_factory=uuid4)
    time: datetime = Field(default_factory=datetime.now)

    _repeat_last: ClassVar[Response | None] = None  # static instance

    @classproperty
    def repeat_last(cls) -> Response:
        if not Response._repeat_last:
            Response._repeat_last = Response()
            return Response._repeat_last
        return Response._repeat_last

    class Config:
        arbitrary_types_allowed = True

    def __eq__(self, other):
        return self.id == other.id


class ResponseHandler(Protocol):
    def respond(self, response: Response):
        pass

    def unrespond(self, response: Response):
        pass

    def pop_context(self):
        pass


class AsyncResponseHandler(Protocol):
    async def respond(self, response: Response):
        pass

    async def unrespond(self, response: Response):
        pass

    async def pop_context(self):
        pass
