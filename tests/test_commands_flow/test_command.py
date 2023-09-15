import pytest
from core import CommandsManager, Response


@pytest.mark.anyio
async def test_call_async_command_from_command():
    manager = CommandsManager()
    
    @manager.new('foo')
    async def foo() -> Response: 
        return Response(text = 'foo!')
    
    @manager.new('bar')
    async def bar() -> Response: 
        return await foo()
    
    assert (await bar()).text == 'foo!'
