from typing import cast

import anyio
import asyncer
import pytest

from stark.core.command import Response
from stark.core.commands_context import CommandsContext
from stark.core.commands_context_processor import CommandsContextLayer, CommandsContextProcessor, RecognizedEntity
from stark.core.commands_manager import CommandsManager, SearchResult
from stark.core.patterns.pattern import Pattern
from stark.core.types.object import Object
from stark.general.classproperty import classproperty


class Location(Object[str]):
    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern("**")


@pytest.fixture
def manager():
    return CommandsManager()


@pytest.fixture
async def new_context(manager):
    async with asyncer.create_task_group() as main_task_group:
        cc = CommandsContext(main_task_group, manager)
        cc.pattern_parser.register_parameter_type(Location)
        yield cc


async def test_context_param(new_context, manager):
    location: Location | None = None
    location = cast(Location, location)

    @manager.new("go to $destination:Location")
    def go_to(destination: Location) -> Response:
        nonlocal location
        location = destination
        return Response(text=f"Going to {destination.value}")

    @manager.new("let's go")
    def lets_go(destination: Location | None) -> Response:
        nonlocal location
        location = destination
        if destination:
            return Response(text=f"Going to {destination.value}")
        else:
            return Response(text="Where to?")

    layer = CommandsContextLayer(commands=[go_to, lets_go], parameters={"destination": Location("context_place")})
    new_context.context_queue.insert(0, layer)

    results = await new_context.process_string("go to the place")
    assert len(results) == 1
    await anyio.sleep(0.01)
    assert location and location.value == "the place"
    location = None

    results = await new_context.process_string("let's go")
    assert len(results) == 1
    await anyio.sleep(0.01)
    assert location and location.value == "context_place"

    results = await new_context.process_string("go to")
    assert not results


async def test_ner(new_context, manager):
    location: Location | None = None
    location = cast(Location, location)

    @manager.new("go to $destination:Location")
    def go_to(destination: Location) -> Response:
        nonlocal location
        location = destination
        return Response(text=f"Going to {destination.value}")

    class FakeNERProcessor(CommandsContextProcessor):
        async def process_string(
            self, string: str, context: CommandsContext, recognized_entities: list[RecognizedEntity]
        ) -> tuple[list[SearchResult], int]:
            if "London" in string:
                recognized_entities.append(RecognizedEntity(substring="London", type=Location))
            return [], 0

    await new_context.process_string("go to the famous London city")
    await anyio.sleep(0.01)
    assert location and location.value == "the famous London city"
    location = None

    new_context.processors.insert(0, FakeNERProcessor())
    await new_context.process_string("go to the famous London city")
    await anyio.sleep(0.01)
    assert location and location.value == "London"
