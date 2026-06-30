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

    @manager.new('turn off the light')
    async def lights_off() -> Response:
        return Response(text = 'Lights off!')

    assert (await lights_off()).text == 'Lights off!'

async def test_call_async_command_from_async_command():
    manager = CommandsManager()

    @manager.new('turn off the light')
    async def lights_off() -> Response:
        return Response(text = 'Lights off!')

    @manager.new('good night')
    async def good_night() -> Response:
        return await lights_off()

    assert (await good_night()).text == 'Lights off!'

async def test_async_command_with_async_response_handler():
    manager = CommandsManager()

    @manager.new('turn off the light')
    async def lights_off(handler: AsyncResponseHandler):
        ...

async def test_async_command_with_sync_response_handler():
    manager = CommandsManager()

    with pytest.raises(TypeError, match = '`ResponseHandler` is not compatible with command .* because it is async, use `AsyncResponseHandler` instead'):
        @manager.new('turn off the light')
        async def lights_off(handler: ResponseHandler):
            ...

async def test_async_command_generator_yielding_response():
    manager = CommandsManager()

    @manager.new('turn off the light')
    async def lights_off() -> AsyncGenerator[Response, None]:
        yield Response(text = 'Lights off!')

    i = 0
    async for response in await lights_off():
        assert response.text == 'Lights off!'
        i += 1
    assert i == 1

async def test_async_command_generator_multiple_yielding_response():
    manager = CommandsManager()

    @manager.new('start timer')
    async def start_timer() -> AsyncGenerator[Response, None]:
        yield Response(text = 'Timer started')
        yield Response(text = 'Timer 50% done')
        yield Response(text = 'Timer finished')

    expected = ['Timer started', 'Timer 50% done', 'Timer finished']

    async for response in await start_timer():
        assert response.text == expected.pop(0)

    assert not expected

async def test_exception_in_command():
    manager = CommandsManager()

    @manager.new('turn off the light')
    async def lights_off() -> Response:
        raise Exception('smart bulb not responding')

    # with pytest.raises(Exception, match = 'smart bulb not responding'):
    #     await lights_off()

    assert (await lights_off()).status == ResponseStatus.error
