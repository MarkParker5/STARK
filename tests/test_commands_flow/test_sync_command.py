import pytest
from asyncer import syncify
from core import CommandsManager, Response


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
