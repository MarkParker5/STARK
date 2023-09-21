from typing import AsyncGenerator
import pytest
from stark.core import (
    CommandsManager,
    Response,
    ResponseHandler,
    AsyncResponseHandler,
    ResponseStatus
)


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

async def test_async_command_generator_yielding_response():
    manager = CommandsManager()
    
    @manager.new('foo')
    async def foo() -> AsyncGenerator[Response, None]:
        yield Response(text = 'foo!')
    
    i = 0
    async for response in await foo():
        assert response.text == 'foo!'
        i += 1
    assert i == 1

async def test_async_command_generator_multiple_yielding_response():
    manager = CommandsManager()
    
    @manager.new('foo')
    async def foo() -> AsyncGenerator[Response, None]: 
        yield Response(text = 'foo!')
        yield Response(text = 'bar!')
        yield Response(text = 'baz!')
    
    expected = ['foo!', 'bar!', 'baz!']
    
    async for response in await foo():
        assert response.text == expected.pop(0)

    assert not expected

async def test_exception_in_command():
    manager = CommandsManager()
    
    @manager.new('foo')
    async def foo() -> Response: 
        raise Exception('foo exception')
    
    # with pytest.raises(Exception, match = 'foo exception'):
    #     await foo()
    
    assert (await foo()).status == ResponseStatus.error
