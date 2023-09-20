import pytest
import warnings
import anyio
from stark.core import Response, ResponseHandler, AsyncResponseHandler


async def test_command_return_response(commands_context_flow, autojump_clock):
    async with commands_context_flow() as (manager, context, context_delegate):
    
        @manager.new('foo')
        async def foo() -> Response: 
            return Response(text = 'foo!')
        
        await context.process_string('foo')
        await anyio.sleep(5)

        assert len(context_delegate.responses) == 1
        assert context_delegate.responses[0].text == 'foo!'

async def test_sync_command_call_sync_respond(commands_context_flow, autojump_clock):
    async with commands_context_flow() as (manager, context, context_delegate):
    
        @manager.new('foo')
        def foo(handler: ResponseHandler): 
            handler.respond(Response(text = 'foo!'))
        
        await context.process_string('foo')
        await anyio.sleep(5)

        assert len(context_delegate.responses) == 1
        assert context_delegate.responses[0].text == 'foo!'

async def test_async_command_call_sync_respond(commands_context_flow, autojump_clock):
    async with commands_context_flow() as (manager, context, context_delegate):
        
        @manager.new('foo')
        async def foo(handler: AsyncResponseHandler): 
            await handler.respond(Response(text = 'foo!'))
        
        await context.process_string('foo')
        await anyio.sleep(5)

        assert len(context_delegate.responses) == 1
        assert context_delegate.responses[0].text == 'foo!'

@pytest.mark.skip(reason = 'deprecated: added checks for DI on command creation')
async def test_sync_command_call_async_respond(commands_context_flow, autojump_clock):
    async with commands_context_flow() as (manager, context, context_delegate):
        
        @manager.new('foo')
        def foo(handler: AsyncResponseHandler): 
            with warnings.catch_warnings(record = True) as warnings_list:
                assert len(warnings_list) == 0
                handler.respond(Response(text = 'foo!')) # type: ignore
                assert len(warnings_list) == 1
                assert issubclass(warnings_list[0].category, RuntimeWarning)
                assert 'was never awaited' in str(warnings_list[0].message)
        
        await context.process_string('foo')
        await anyio.sleep(5)

        assert len(context_delegate.responses) == 0

@pytest.mark.skip(reason = 'deprecated: added checks for DI on command creation')
async def test_async_command_call_async_respond(commands_context_flow, autojump_clock):
    async with commands_context_flow() as (manager, context, context_delegate):
        
        @manager.new('foo')
        async def foo(handler: ResponseHandler):
            with pytest.raises(RuntimeError, match = 'can only be run from an AnyIO worker thread'):
                handler.respond(Response(text = 'foo!'))
        
        await context.process_string('foo')
        await anyio.sleep(5)

        assert len(context_delegate.responses) == 0

async def test_command_multiple_respond(commands_context_flow, autojump_clock):
    async with commands_context_flow() as (manager, context, context_delegate):
        
        @manager.new('foo')
        async def foo(handler: AsyncResponseHandler): 
            await anyio.sleep(2)
            await handler.respond(Response(text = 'foo0'))
            await anyio.sleep(2)
            await handler.respond(Response(text = 'foo1'))
            await anyio.sleep(2)
            await handler.respond(Response(text = 'foo2'))
            await anyio.sleep(2)
            await handler.respond(Response(text = 'foo3'))
            await anyio.sleep(2)
            return Response(text = 'foo4')
        
        await context.process_string('foo')
        
        last_count = 0
        while last_count < 5:
            await anyio.sleep(1)
            if last_count == len(context_delegate.responses): continue
            assert len(context_delegate.responses) == last_count + 1
            last_count += 1
            assert context_delegate.responses[last_count - 1].text == f'foo{last_count - 1}'
            
        assert len(context_delegate.responses) == 5
        assert [r.text for r in context_delegate.responses] == [f'foo{i}' for i in range(5)]
