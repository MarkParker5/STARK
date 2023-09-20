from typing import Generator
import warnings
import pytest
from asyncer import syncify
from stark.core import CommandsManager, Response, ResponseHandler, AsyncResponseHandler


async def test_create_await_run_sync_command():
    manager = CommandsManager()

    @manager.new('foo')
    def foo() -> Response: 
        return Response(text = 'foo!')

    # commands are always async, no matter runner function is sync or async
    # so we need to await or syncify them
    assert (await foo()).text == 'foo!'
    
def test_create_syncify_run_sync_command():
    manager = CommandsManager()

    @manager.new('foo')
    def foo() -> Response: 
        return Response(text = 'foo!')

    # commands are always async, no matter runner function is sync or async
    # so we need to await or syncify them
    # raise_sync_error needs for tests only because test function doesn't run in worker thread
    sync_foo = syncify(foo, raise_sync_error = False)
    assert sync_foo().text == 'foo!'

async def test_call_sync_command_from_sync_command_await():
    manager = CommandsManager()
    
    @manager.new('foo')
    def foo() -> Response: 
        return Response(text = 'foo!')
    
    @manager.new('bar')
    def bar() -> Response: 
        # commands are always async, so we need to syncify async foo (or delcare current function as async and await foo, check /choice-runner-type)
        sync_foo = syncify(foo)
        return sync_foo()
    
    assert (await bar()).text == 'foo!'

def test_call_sync_command_from_sync_command_syncify():
    manager = CommandsManager()
    
    @manager.new('foo')
    def foo() -> Response: 
        return Response(text = 'foo!')
    
    @manager.new('bar')
    def bar() -> Response: 
        # commands are always async, so we need to syncify async foo (or delcare current function as async and await foo, check /choice-runner-type)
        sync_foo = syncify(foo)
        return sync_foo()
    
    # raise_sync_error needs for tests only because test function doesn't run in worker thread
    sync_bar = syncify(bar, raise_sync_error = False)
    assert sync_bar().text == 'foo!'

def test_sync_command_with_sync_response_handler():
    manager = CommandsManager()
    
    @manager.new('foo')
    def foo(handler: ResponseHandler): 
        ...
    
def test_sync_command_with_async_response_handler():
    manager = CommandsManager()
    
    with pytest.raises(TypeError, match = '`AsyncResponseHandler` is not compatible with command .* because it is sync, use `ResponseHandler` instead'):
        @manager.new('foo')
        def foo(handler: AsyncResponseHandler): 
            ...
            
async def test_sync_command_generator_yielding_response():
    manager = CommandsManager()
    
    with warnings.catch_warnings(record = True) as warnings_list:
        @manager.new('foo')
        def foo() -> Generator[Response, None, None]: 
            yield Response(text = 'foo!')
        
        assert next(await foo()).text == 'foo!'
        
        assert len(warnings_list) == 1
        assert issubclass(warnings_list[0].category, UserWarning)
        assert 'GeneratorType that is not fully supported and may block the main thread' in str(warnings_list[0].message)
    
async def test_sync_command_generator_multiple_yielding_response():
    manager = CommandsManager()
    
    with warnings.catch_warnings(record = True) as warnings_list:
        @manager.new('foo')
        def foo() -> Generator[Response, None, None]: 
            yield Response(text = 'foo!')
            yield Response(text = 'bar!')
            yield Response(text = 'baz!')
        
        expected = ['foo!', 'bar!', 'baz!']
        for response in await foo(): # TODO: make generator async generator and use async for
            assert response.text == expected.pop(0)
            
        assert len(warnings_list) == 1
        assert issubclass(warnings_list[0].category, UserWarning)
        assert 'GeneratorType that is not fully supported and may block the main thread' in str(warnings_list[0].message)
