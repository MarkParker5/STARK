import re
import pytest
from VICore import CommandsManager, VIWord


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
    
    with pytest.raises(AssertionError, match = re.escape('Command CommandsManager.test must have all parameters from pattern:')):
        @manager.new('test $name:VIWord, $secondName:VIWord')
        def test(name: VIWord): pass
    
def test_search():
    manager = CommandsManager()
    
    @manager.new('test')
    def test(): pass
    
    @manager.new('hello $name:VIWord')
    def hello(name: VIWord): pass
    
    @manager.new('hello $name:VIWord $surname:VIWord')
    def hello2(name: VIWord, surname: VIWord): pass
    
    # test
    result = manager.search('test')
    assert result is not None
    assert len(result) == 1
    assert result[0].command.name == 'CommandsManager.test'
    
    # hello
    result = manager.search('hello world')
    assert result is not None
    assert len(result) == 1
    assert result[0].command.name == 'CommandsManager.hello'
    assert result[0].substring == 'hello world'
    assert type(result[0].parameters['name']) is VIWord
    assert result[0].parameters['name'].value == 'world'
    
    # hello2
    result = manager.search('hello new world')
    assert result is not None
    assert len(result) == 2
    assert hello in [result[0].command, result[1].command] and hello2 in [result[0].command, result[1].command]
    
    for result in result:
        if result.command == hello:
            assert result.substring == 'hello new'
        elif result.command == hello2:
            assert result.substring == 'hello new world'
            assert result.parameters == {'name': VIWord('new'), 'surname': VIWord('world')}
            
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
    