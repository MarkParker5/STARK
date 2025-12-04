import logging

logging.getLogger("faker").setLevel(logging.WARNING)

import contextlib
from typing import AsyncGenerator

import anyio
import asyncer
import pytest

from stark.core import (
    AsyncResponseHandler,
    CommandsContext,
    CommandsContextDelegate,
    CommandsManager,
    Response,
    ResponseHandler,
)
from stark.core.types import Word
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
    async def _commands_context_flow() -> AsyncGenerator[tuple[CommandsManager, CommandsContext, CommandsContextDelegateMock], None]:
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
    async def _commands_context_flow_filled() -> AsyncGenerator[tuple[CommandsContext, CommandsContextDelegateMock], None]:
        async with commands_context_flow() as (manager, context, context_delegate):

            @manager.new("test")
            def test():
                text = voice = "test"
                return Response(text=text, voice=voice)

            @manager.new("lorem * dolor")
            def lorem():
                return Response(text="Lorem!", voice="Lorem!")

            @manager.new("hello", hidden=True)
            def hello_context(**params):
                voice = text = f"Hi, {params['name']}!"
                return Response(text=text, voice=voice)

            @manager.new("bye", hidden=True)
            def bye_context(name: Word, handler: ResponseHandler):
                handler.pop_context()
                return Response(text=f"Bye, {name}!")

            @manager.new("hello $name:Word")
            def hello(name: Word):
                text = voice = f"Hello, {name}!"
                return Response(
                    text=text,
                    voice=voice,
                    commands=[hello_context, bye_context],
                    parameters={"name": name},
                )

            @manager.new("repeat")
            def repeat():
                return Response.repeat_last

            # background commands

            @manager.new("background min")
            async def background(handler: AsyncResponseHandler):
                text = voice = "Starting background task"
                await handler.respond(Response(text=text, voice=voice))
                await anyio.sleep(1)
                text = voice = "Finished background task"
                return Response(text=text, voice=voice)

            @manager.new("background needs input")
            async def background_needs_input(handler: AsyncResponseHandler):
                await anyio.sleep(1)

                for text in ["First response", "Second response", "Third response"]:
                    await handler.respond(Response(text=text, voice=text))

                text = "Needs input"
                await handler.respond(Response(text=text, voice=text, needs_user_input=True))

                for text in ["Fourth response", "Fifth response", "Sixth response"]:
                    await handler.respond(Response(text=text, voice=text))

                text = voice = "Finished long background task"
                return Response(text=text, voice=voice)

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
                response = Response(text="Deleted response", voice="Deleted response")
                await handler.respond(response)
                await anyio.sleep(1)
                await handler.unrespond(response)
                return None

            yield (context, context_delegate)

    return _commands_context_flow_filled


@pytest.fixture
async def voice_assistant(commands_context_flow_filled):
    @contextlib.asynccontextmanager
    async def _voice_assistant() -> AsyncGenerator[VoiceAssistant, None]:
        async with commands_context_flow_filled() as (context, context_delegate):
            voice_assistant = VoiceAssistant(
                speech_recognizer=SpeechRecognizerMock(),
                speech_synthesizer=SpeechSynthesizerMock(),
                commands_context=context,
            )
            yield voice_assistant

    return _voice_assistant


def pytest_addoption(parser):
    parser.addoption("--benchmark", action="store_true", default=False, help="Run benchmark tests")


def pytest_runtest_setup(item):
    if "benchmark" in item.keywords and not item.config.getoption("--benchmark"):
        pytest.skip("skipping benchmark, use --benchmark to run")
