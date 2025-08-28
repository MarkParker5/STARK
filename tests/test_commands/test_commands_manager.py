import re

import pytest

from stark.core import CommandsManager
from stark.core.types import Word


def test_new():
    manager = CommandsManager()
    manager.new('test')(lambda: None)
    assert len(manager.commands) == 1

    @manager.new('foo bar')
    def foo_bar(): pass

    assert len(manager.commands) == 2
    assert manager.commands[1].name == 'CommandsManager.foo_bar'
    assert manager.commands[1].pattern._origin == 'foo bar'

def test_new_with_extra_parameters_in_pattern():
    manager = CommandsManager()

    with pytest.raises(AssertionError, match = re.escape('Command CommandsManager.test must have all parameters from pattern')):
        @manager.new('test $name:Word, $secondName:Word')
        def test(name: Word): pass

async def test_search():
    manager = CommandsManager()

    @manager.new('test')
    def test(): pass

    @manager.new('hello $name:Word $surname:Word')
    def hello2(name: Word, surname: Word): pass

    @manager.new('hello $name:Word')
    def hello(name: Word): pass

    # test
    result = await manager.search('test')
    assert result is not None
    assert len(result) == 1
    assert result[0].command.name == 'CommandsManager.test'

    # hello
    result = await manager.search('hello world')
    assert result is not None
    assert len(result) == 1
    assert result[0].command.name == 'CommandsManager.hello'
    assert result[0].match_result.substring == 'hello world'
    assert type(result[0].match_result.parameters['name']) is Word
    assert result[0].match_result.parameters['name'].value == 'world'

    # hello2
    result = await manager.search('hello new world')
    assert result is not None
    assert len(result) == 1
    assert result[0].command == hello2
    assert result[0].match_result.substring == 'hello new world'
    assert result[0].match_result.parameters == {'name': Word('new'), 'surname': Word('world')}

def test_extend_manager():
    root_manager = CommandsManager()
    child_manager = CommandsManager('Child')

    @root_manager.new('test')
    def test(): pass

    @child_manager.new('test')
    def test(): pass

    assert len(child_manager.commands) == 1
    assert len(root_manager.commands) == 1
    assert child_manager.commands[0].name == 'Child.test'
    assert root_manager.commands[0].name == 'CommandsManager.test'

    root_manager.extend(child_manager)

    assert len(child_manager.commands) == 1
    assert len(root_manager.commands) == 2
    assert child_manager.commands[0].name == 'Child.test'
    assert root_manager.commands[0].name == 'CommandsManager.test'
    assert root_manager.commands[1].name == 'Child.test'

def test_manager_get_command_by_name():
    manager = CommandsManager('TestManager')
    child = CommandsManager('Child')

    @manager.new('')
    def test(): ...

    @manager.new('')
    def test2(): ...

    @manager.new('')
    def test3(): ...

    @manager.new('')
    def test4(): ...

    @child.new('')
    def test5(): ...

    manager.extend(child)

    assert manager.get_by_name('test2') == test2
    assert manager.get_by_name('TestManager.test3') == test3
    assert manager.get_by_name('test5') == None
    assert manager.get_by_name('Child.test5') == test5
