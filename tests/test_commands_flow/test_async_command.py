import pytest
from core import CommandsManager, Response


async def test_create_run_async_command():
    manager = CommandsManager()
    
    @manager.new('foo')
    async def foo() -> Response: 
        return Response(text = 'foo!')
    
    assert (await foo()).text == 'foo!'

async def test_call_async_command_from_async_command():
    manager = CommandsManager()
    
    @manager.new('foo')
    async def foo() -> Response: 
        return Response(text = 'foo!')
    
    @manager.new('bar')
    async def bar() -> Response: 
        return await foo()
    
    assert (await bar()).text == 'foo!'
