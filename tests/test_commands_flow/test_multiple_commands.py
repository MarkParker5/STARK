import pytest
import anyio
from stark.core import Pattern, Response, CommandsManager
from stark.core.types import Object
from stark.general.classproperty import classproperty
import random


async def test_multiple_commands(commands_context_flow, autojump_clock):
    async with commands_context_flow() as (manager, context, context_delegate):
    
        @manager.new('foo bar')
        def foobar(): 
            return Response(text = 'foo!')
        
        @manager.new('lorem * dolor')
        def lorem(): 
            return Response(text = 'lorem!')
        
        await context.process_transcription('foo bar lorem ipsum dolor')
        await anyio.sleep(5)

        assert len(context_delegate.responses) == 2
        assert {context_delegate.responses[0].text, context_delegate.responses[1].text} == {'foo!', 'lorem!'}

async def test_repeating_command(commands_context_flow, autojump_clock):
    async with commands_context_flow() as (manager, context, context_delegate):
    
        @manager.new('lorem * dolor')
        def lorem(): 
            return Response(text = 'lorem!')
        
        await context.process_transcription('lorem pisum dolor lorem ipsutest_repeating_commanduum dolor sit amet')
        await anyio.sleep(5)
        
        assert len(context_delegate.responses) == 2
        assert context_delegate.responses[0].text == 'lorem!'
        assert context_delegate.responses[1].text == 'lorem!'

async def test_overlapping_commands_less_priority_cut(commands_context_flow, autojump_clock):
    manager = CommandsManager()

    @manager.new('foo bar *')
    def foobar(): 
        return Response(text = 'foo!')
    
    @manager.new('* baz')
    def baz(): 
        return Response(text = 'baz!')
    
    result = await manager.search('foo bar test baz')
    assert len(result) == 2
    assert result[0].match_result.substring == 'foo bar test'
    assert result[1].match_result.substring == 'baz'

async def test_overlapping_commands_priority_cut(commands_context_flow, autojump_clock):
    manager = CommandsManager()
    
    @manager.new('foo bar *')
    def foobar(): 
        return Response(text = 'foo!')
    
    @manager.new('*t baz')
    def baz(): 
        return Response(text = 'baz!')
    
    result = await manager.search('foo bar test baz')
    
    assert len(result) == 2
    assert result[0].match_result.substring == 'foo bar'
    assert result[1].match_result.substring == 'test baz'

async def test_overlapping_commands_remove(commands_context_flow, autojump_clock):
    manager = CommandsManager()
    
    @manager.new('foo bar')
    def foobar(): 
        return Response(text = 'foo!')
    
    @manager.new('bar baz')
    def barbaz(): 
        return Response(text = 'baz!')
    
    result = await manager.search('foo bar baz')
    assert len(result) == 1
    assert result[0].command == foobar
    
async def test_overlapping_commands_remove_inverse(commands_context_flow, autojump_clock):
    manager = CommandsManager()
     
    @manager.new('bar baz')
    def barbaz(): 
        return Response(text = 'baz!')
    
    @manager.new('foo bar')
    def foobar(): 
        return Response(text = 'foo!')
    
    result = await manager.search('foo bar baz')
    assert len(result) == 1
    assert result[0].command == barbaz
    
@pytest.mark.skip(reason = 'Cache is deprecated and not working properly anymore because of new concurrent algorithm; need new async lru cache implementation')
async def test_objects_parse_caching(commands_context_flow, autojump_clock):
    class Mock(Object):
    
        parsing_counter = 0
        
        @classproperty
        def pattern(cls):
            return Pattern('*')
        
        async def did_parse(self, from_string: str) -> str:
            Mock.parsing_counter += 1
            return from_string
    
    mock_name = f'Mock{random.randint(0, 10**10)}'
    Mock.__name__ = mock_name # prevent name collision on paralell tests
    
    manager = CommandsManager()
    Pattern.add_parameter_type(Mock)
    
    @manager.new(f'hello $mock:{mock_name}')
    def hello(mock: Mock): pass
    
    @manager.new(f'hello $mock:{mock_name} 2')
    def hello2(mock: Mock): pass
    
    @manager.new(f'hello $mock:{mock_name} 22')
    def hello22(mock: Mock): pass
    
    @manager.new(f'test $mock:{mock_name}')
    async def test(mock: Mock): pass
    
    assert Mock.parsing_counter == 0
    await manager.search('hello foobar 22')
    assert Mock.parsing_counter == 1
    await manager.search('hello foobar 22')
    assert Mock.parsing_counter == 2
