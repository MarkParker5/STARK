from VICore import CommandsManager, VIWord


def test_new():
    manager = CommandsManager()
    manager.new(['test'])(lambda: None)
    assert len(manager.commands) == 1
    
    @manager.new(['foo bar'])
    def foo_bar(): pass
    
    assert len(manager.commands) == 2
    assert manager.commands[1].name == 'foo_bar'
    assert manager.commands[1].patterns[0]._origin == 'foo bar'
    
def test_search():
    manager = CommandsManager()
    
    @manager.new(['test'])
    def test(): pass
    
    @manager.new(['hello $name:VIWord'])
    def hello(): pass
    
    @manager.new(['hello $name:VIWord $surname:VIWord'])
    def hello2(): pass
    
    # test
    result = manager.search('test')
    assert result is not None
    assert len(result) == 1
    assert result[0].command.name == 'test'
    
    # hello
    result = manager.search('hello world')
    assert result is not None
    assert len(result) == 1
    assert result[0].command.name == 'hello'
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
            