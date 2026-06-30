import pytest
import warnings
import anyio
from stark.core import Response, ResponseHandler, AsyncResponseHandler


async def test_command_return_response(commands_context_flow, autojump_clock):
    async with commands_context_flow() as (manager, context, context_delegate):
    
        @manager.new('turn off the light')
        async def lights_off() -> Response:
            return Response(text = 'Lights off!')

        await context.process_string('turn off the light')
        await anyio.sleep(5)

        assert len(context_delegate.responses) == 1
        assert context_delegate.responses[0].text == 'Lights off!'

async def test_sync_command_call_sync_respond(commands_context_flow, autojump_clock):
    async with commands_context_flow() as (manager, context, context_delegate):
    
        @manager.new('turn off the light')
        def lights_off(handler: ResponseHandler):
            handler.respond(Response(text = 'Lights off!'))

        await context.process_string('turn off the light')
        await anyio.sleep(5)

        assert len(context_delegate.responses) == 1
        assert context_delegate.responses[0].text == 'Lights off!'

async def test_async_command_call_sync_respond(commands_context_flow, autojump_clock):
    async with commands_context_flow() as (manager, context, context_delegate):

        @manager.new('turn off the light')
        async def lights_off(handler: AsyncResponseHandler):
            await handler.respond(Response(text = 'Lights off!'))

        await context.process_string('turn off the light')
        await anyio.sleep(5)

        assert len(context_delegate.responses) == 1
        assert context_delegate.responses[0].text == 'Lights off!'

@pytest.mark.skip(reason = 'deprecated: added checks for DI on command creation')
async def test_sync_command_call_async_respond(commands_context_flow, autojump_clock):
    async with commands_context_flow() as (manager, context, context_delegate):
        
        @manager.new('turn off the light')
        def lights_off(handler: AsyncResponseHandler):
            with warnings.catch_warnings(record = True) as warnings_list:
                assert len(warnings_list) == 0
                handler.respond(Response(text = 'Lights off!')) # type: ignore
                assert len(warnings_list) == 1
                assert issubclass(warnings_list[0].category, RuntimeWarning)
                assert 'was never awaited' in str(warnings_list[0].message)

        await context.process_string('turn off the light')
        await anyio.sleep(5)

        assert len(context_delegate.responses) == 0

@pytest.mark.skip(reason = 'deprecated: added checks for DI on command creation')
async def test_async_command_call_async_respond(commands_context_flow, autojump_clock):
    async with commands_context_flow() as (manager, context, context_delegate):

        @manager.new('turn off the light')
        async def lights_off(handler: ResponseHandler):
            with pytest.raises(RuntimeError, match = 'can only be run from an AnyIO worker thread'):
                handler.respond(Response(text = 'Lights off!'))

        await context.process_string('turn off the light')
        await anyio.sleep(5)

        assert len(context_delegate.responses) == 0

async def test_command_multiple_respond(commands_context_flow, autojump_clock):
    async with commands_context_flow() as (manager, context, context_delegate):
        
        @manager.new('start timer')
        async def start_timer(handler: AsyncResponseHandler):
            await anyio.sleep(2)
            await handler.respond(Response(text = 'Timer update 0'))
            await anyio.sleep(2)
            await handler.respond(Response(text = 'Timer update 1'))
            await anyio.sleep(2)
            await handler.respond(Response(text = 'Timer update 2'))
            await anyio.sleep(2)
            await handler.respond(Response(text = 'Timer update 3'))
            await anyio.sleep(2)
            return Response(text = 'Timer update 4')

        await context.process_string('start timer')

        last_count = 0
        while last_count < 5:
            await anyio.sleep(1)
            if last_count == len(context_delegate.responses): continue
            assert len(context_delegate.responses) == last_count + 1
            last_count += 1
            assert context_delegate.responses[last_count - 1].text == f'Timer update {last_count - 1}'

        assert len(context_delegate.responses) == 5
        assert [r.text for r in context_delegate.responses] == [f'Timer update {i}' for i in range(5)]
