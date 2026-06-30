from stark.core import CommandsManager
from stark.core.parsing import PatternParser
from stark.core.processors import SearchProcessor
from stark.core.types import Word

pattern_parser = PatternParser()


def test_new():
    manager = CommandsManager()
    manager.new("set alarm")(lambda: None)
    assert len(manager.commands) == 1

    @manager.new("play music")
    def play_music():
        pass

    assert len(manager.commands) == 2
    assert manager.commands[1].name == "CommandsManager.play_music"
    assert manager.commands[1].get_pattern("base")._origin == "play music"


async def test_search():
    manager = CommandsManager()

    @manager.new("set alarm")
    def set_alarm():
        pass

    @manager.new("hello $name:Word $surname:Word")
    def hello2(name: Word, surname: Word):
        pass

    @manager.new("hello $name:Word")
    def hello(name: Word):
        pass

    # set alarm
    result = await SearchProcessor().search("set alarm", pattern_parser, manager.commands, [])
    assert result is not None
    assert len(result) == 1
    assert result[0].command.name == "CommandsManager.set_alarm"

    # hello
    result = await SearchProcessor().search("hello world", pattern_parser, manager.commands, [])
    assert result is not None
    assert len(result) == 1
    assert result[0].command.name == "CommandsManager.hello"
    assert result[0].match_result.parameters["name"].value == "world"

    # hello2
    result = await SearchProcessor().search("hello new world", pattern_parser, manager.commands, [])
    assert result is not None
    assert len(result) == 1
    assert result[0].command == hello2
    assert result[0].match_result.substring == "hello new world"
    assert result[0].match_result.parameters == {
        "name": Word("new"),
        "surname": Word("world"),
    }


def test_extend_manager():
    root_manager = CommandsManager()
    child_manager = CommandsManager("Child")

    @root_manager.new("set alarm")
    def set_alarm():
        pass

    @child_manager.new("set alarm")
    def set_alarm():
        pass

    assert len(child_manager.commands) == 1
    assert len(root_manager.commands) == 1
    assert child_manager.commands[0].name == "Child.set_alarm"
    assert root_manager.commands[0].name == "CommandsManager.set_alarm"

    root_manager.extend(child_manager)

    assert len(child_manager.commands) == 1
    assert len(root_manager.commands) == 2
    assert child_manager.commands[0].name == "Child.set_alarm"
    assert root_manager.commands[0].name == "CommandsManager.set_alarm"
    assert root_manager.commands[1].name == "Child.set_alarm"


def test_manager_get_command_by_name():
    manager = CommandsManager("TestManager")
    child = CommandsManager("Child")

    @manager.new("")
    def lock_door(): ...

    @manager.new("")
    def unlock_door(): ...

    @manager.new("")
    def open_garage(): ...

    @manager.new("")
    def close_garage(): ...

    @child.new("")
    def ring_doorbell(): ...

    manager.extend(child)

    assert manager.get_by_name("unlock_door") == unlock_door
    assert manager.get_by_name("TestManager.open_garage") == open_garage
    assert manager.get_by_name("ring_doorbell") == None
    assert manager.get_by_name("Child.ring_doorbell") == ring_doorbell
