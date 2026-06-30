import json
from typing import Any, AsyncGenerator, Callable, Type

from stark.core import CommandsManager, Response
from stark.core.types import Word
from stark.general.json_encoder import StarkJsonEncoder


async def test_command_json():
    manager = CommandsManager("TestManager")

    @manager.new("play $song:Word")
    def play(track: str, song: Word, volume: int | None = None) -> Response:
        """play a song"""
        return Response(track)

    string = json.dumps(play, cls=StarkJsonEncoder)
    parsed = json.loads(string)

    assert parsed["name"] == "TestManager.play"
    assert parsed["patterns"]["base"]["origin"] == r"play $song:Word"
    assert parsed["declaration"] == "def play(track: str, song: Word, volume: int | None = None) -> Response"
    assert parsed["docstring"] == "play a song"


async def test_async_command_complicate_type_json():
    manager = CommandsManager("TestManager")

    @manager.new("get forecast")
    async def get_forecast(some: AsyncGenerator[Callable[[Any], Type], list[None]]):
        return Response()

    string = json.dumps(get_forecast, cls=StarkJsonEncoder)
    parsed = json.loads(string)

    assert parsed["name"] == "TestManager.get_forecast"
    assert parsed["patterns"]["base"]["origin"] == r"get forecast"
    assert parsed["declaration"] == "async def get_forecast(some: AsyncGenerator)"  # TODO: improve AsyncGenerator to full type
    # assert parsed['declaration'] == 'async def get_forecast(some: AsyncGenerator[Callable[[Any], Type], list[None], None])'
    assert parsed["docstring"] == ""


def test_manager_json():

    manager = CommandsManager("TestManager")

    @manager.new("")
    def lights_off(): ...

    @manager.new("")
    def play_music(): ...

    @manager.new("")
    def set_alarm(): ...

    @manager.new("")
    def get_forecast(): ...

    string = json.dumps(manager, cls=StarkJsonEncoder)
    parsed = json.loads(string)

    assert parsed["name"] == "TestManager"
    assert {c["name"] for c in parsed["commands"]} == {
        "TestManager.lights_off",
        "TestManager.play_music",
        "TestManager.set_alarm",
        "TestManager.get_forecast",
    }
