import pytest
from core import CommandsManager, Response, ResponseHandler, AsyncResponseHandler


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
    
async def test_async_command_with_async_response_handler():
    mamnager = CommandsManager()
    
    @mamnager.new('foo')
    async def foo(handler: AsyncResponseHandler): 
        ...

async def test_async_command_with_sync_response_handler():
    manager = CommandsManager()
    
    with pytest.raises(TypeError, match = '`ResponseHandler` is not compatible with command .* because it is async, use `AsyncResponseHandler` instead'):
        @manager.new('foo')
        async def foo(handler: ResponseHandler): 
            ...
