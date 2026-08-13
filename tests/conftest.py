import logging

logging.getLogger("faker").setLevel(logging.WARNING)

import contextlib
from collections.abc import AsyncGenerator

import anyio
import asyncer
import pytest

from stark.core import (
    AsyncResponseHandler,
    CommandsContext,
    CommandsContextDelegate,
    CommandsManager,
    Response,
)
from stark.core.types import NLWord
from stark.general.dependencies import DependencyManager
from stark.interfaces.protocols import SpeechRecognizerDelegate
from stark.voice_assistant import VoiceAssistant


class CommandsContextDelegateMock(CommandsContextDelegate):
    responses: list[Response]

    def __init__(self):
        self.responses = []

    async def commands_context_did_receive_response(self, response: Response):
        self.responses.append(response)

    async def remove_response(self, response: Response):
        self.responses.remove(response)


class SpeechRecognizerMock:
    is_recognizing: bool = False
    delegate: SpeechRecognizerDelegate | None = None

    def microphone_did_receive_sample(self, data):
        pass

    async def start_listening(self):
        pass

    def stop_listening(self):
        pass


class SpeechSynthesizerResultMock:
    async def play(self):
        pass

    def __init__(self, text: str):
        self.text = text


class SpeechSynthesizerMock:
    def __init__(self):
        self.results = []

    async def synthesize(self, text: str) -> SpeechSynthesizerResultMock:
        result = SpeechSynthesizerResultMock(text)
        self.results.append(result)
        return result


@pytest.fixture
async def commands_context_flow():
    @contextlib.asynccontextmanager
    async def _commands_context_flow() -> AsyncGenerator[
        tuple[CommandsManager, CommandsContext, CommandsContextDelegateMock], None
    ]:
        async with asyncer.create_task_group() as main_task_group:
            dependencies = DependencyManager()
            manager = CommandsManager()
            context = CommandsContext(main_task_group, manager, dependencies)
            context_delegate = CommandsContextDelegateMock()
            context.delegate = context_delegate

            assert len(context_delegate.responses) == 0
            assert len(context.context_queue) == 1

            main_task_group.soonify(context.handle_responses)()
            yield (manager, context, context_delegate)
            context.stop()

    return _commands_context_flow


@pytest.fixture
async def commands_context_flow_filled(commands_context_flow):
    @contextlib.asynccontextmanager
    async def _commands_context_flow_filled() -> AsyncGenerator[
        tuple[CommandsContext, CommandsContextDelegateMock], None
    ]:
        async with commands_context_flow() as (manager, context, context_delegate):

            @manager.new("ping")
            async def ping():
                text = voice = "pong"
                return Response(text, voice=voice)

            @manager.new("lorem * dolor")
            async def lorem():
                return Response("Lorem!", voice="Lorem!")

            @manager.new("hello", hidden=True)
            async def hello_context(**params):
                voice = text = f"Hi, {params['name']}!"
                return Response(text, voice=voice)

            @manager.new("bye", hidden=True)
            async def bye_context(name: NLWord, handler: AsyncResponseHandler):
                await handler.pop_context()
                return Response(f"Bye, {name}!")

            @manager.new("hello $name:NLWord")
            async def hello(name: NLWord):
                text = voice = f"Hello, {name}!"
                return Response(
                    text=text,
                    voice=voice,
                    commands=[hello_context, bye_context],
                    parameters={"name": name},
                )

            @manager.new("repeat")
            async def repeat():
                return Response.repeat_last

            # background commands

            @manager.new("background min")
            async def background(handler: AsyncResponseHandler):
                text = voice = "Starting background task"
                await handler.respond(Response(text, voice=voice))
                await anyio.sleep(1)
                text = voice = "Finished background task"
                return Response(text, voice=voice)

            @manager.new("background needs input")
            async def background_needs_input(handler: AsyncResponseHandler):
                await anyio.sleep(1)

                for text in ["First response", "Second response", "Third response"]:
                    await handler.respond(Response(text, voice=text))

                text = "Needs input"
                await handler.respond(Response(text, voice=text, needs_user_input=True))

                for text in ["Fourth response", "Fifth response", "Sixth response"]:
                    await handler.respond(Response(text, voice=text))

                text = voice = "Finished long background task"
                return Response(text, voice=voice)

            @manager.new("background with context")
            async def background_multiple_contexts(handler: AsyncResponseHandler):
                await anyio.sleep(1)
                text = voice = "Finished long background task"
                return Response(
                    text=text,
                    voice=voice,
                    commands=[hello_context, bye_context],
                    parameters={"name": "John"},
                )

            @manager.new("background remove response")
            async def background_remove_response(handler: AsyncResponseHandler):
                response = Response("Deleted response", voice="Deleted response")
                await handler.respond(response)
                await anyio.sleep(1)
                await handler.unrespond(response)

            yield (context, context_delegate)

    return _commands_context_flow_filled


@pytest.fixture
async def voice_assistant(commands_context_flow_filled):
    @contextlib.asynccontextmanager
    async def _voice_assistant() -> AsyncGenerator[VoiceAssistant, None]:
        async with commands_context_flow_filled() as (context, _context_delegate):
            voice_assistant = VoiceAssistant(
                speech_recognizer=SpeechRecognizerMock(),
                speech_synthesizer=SpeechSynthesizerMock(),
                commands_context=context,
            )
            yield voice_assistant

    return _voice_assistant


@pytest.fixture
def wait_responses():
    """Poll in REAL time until `count` responses arrive.

    For the few commands that legitimately run in a worker thread (sync command
    handlers via asyncer.asyncify), the virtual `autojump_clock` can't be used —
    it would jump past the thread's real execution. Those tests use real time and
    this helper instead of a fixed `anyio.sleep`.
    """
    import time

    async def _wait(delegate, count: int, timeout: float = 2.0):
        deadline = time.monotonic() + timeout
        while len(delegate.responses) < count:
            assert time.monotonic() < deadline, (
                f"got {len(delegate.responses)}/{count} responses within {timeout}s"
            )
            await anyio.sleep(0.005)
        return delegate.responses

    return _wait


def pytest_addoption(parser):
    parser.addoption("--benchmark", action="store_true", default=False, help="Run benchmark tests")


def pytest_runtest_setup(item):
    if "benchmark" in item.keywords and not item.config.getoption("--benchmark"):
        pytest.skip("skipping benchmark, use --benchmark to run")  # ty: ignore[too-many-positional-arguments]  # ty stub gap: pytest.skip takes a positional reason
