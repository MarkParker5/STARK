import warnings
from typing import Generator

import pytest
from asyncer import syncify

from stark.core import (
    AsyncResponseHandler,
    CommandsManager,
    Response,
    ResponseHandler,
    ResponseStatus,
)


async def test_create_await_run_sync_command():
    manager = CommandsManager()

    @manager.new('turn off the light')
    def lights_off() -> Response:
        return Response(text = 'Lights off!')

    # commands are always async, no matter runner function is sync or async
    # so we need to await or syncify them
    assert (await lights_off()).text == 'Lights off!'

def test_create_syncify_run_sync_command():
    manager = CommandsManager()

    @manager.new('turn off the light')
    def lights_off() -> Response:
        return Response(text = 'Lights off!')

    # commands are always async, no matter runner function is sync or async
    # so we need to await or syncify them
    # raise_sync_error needs for tests only because test function doesn't run in worker thread
    sync_lights_off = syncify(lights_off, raise_sync_error = False)
    assert sync_lights_off().text == 'Lights off!'

async def test_call_sync_command_from_sync_command_await():
    manager = CommandsManager()

    @manager.new('turn off the light')
    def lights_off() -> Response:
        return Response(text = 'Lights off!')

    @manager.new('good night')
    def good_night() -> Response:
        # commands are always async, so we need to syncify async lights_off (or delcare current function as async and await lights_off, check /choice-runner-type)
        sync_lights_off = syncify(lights_off)
        return sync_lights_off()

    assert (await good_night()).text == 'Lights off!'

def test_call_sync_command_from_sync_command_syncify():
    manager = CommandsManager()

    @manager.new('turn off the light')
    def lights_off() -> Response:
        return Response(text = 'Lights off!')

    @manager.new('good night')
    def good_night() -> Response:
        # commands are always async, so we need to syncify async lights_off (or delcare current function as async and await lights_off, check /choice-runner-type)
        sync_lights_off = syncify(lights_off)
        return sync_lights_off()

    # raise_sync_error needs for tests only because test function doesn't run in worker thread
    sync_good_night = syncify(good_night, raise_sync_error = False)
    assert sync_good_night().text == 'Lights off!'

def test_sync_command_with_sync_response_handler():
    manager = CommandsManager()

    @manager.new('turn off the light')
    def lights_off(handler: ResponseHandler):
        ...

def test_sync_command_with_async_response_handler():
    manager = CommandsManager()

    with pytest.raises(TypeError, match = '`AsyncResponseHandler` is not compatible with command .* because it is sync, use `ResponseHandler` instead'):
        @manager.new('turn off the light')
        def lights_off(handler: AsyncResponseHandler):
            ...

async def test_sync_command_generator_yielding_response():
    manager = CommandsManager()

    with warnings.catch_warnings(record = True) as warnings_list:
        @manager.new('turn off the light')
        def lights_off() -> Generator[Response, None, None]:
            yield Response(text = 'Lights off!')

        assert next(await lights_off()).text == 'Lights off!'

        assert len(warnings_list) == 1
        assert issubclass(warnings_list[0].category, UserWarning)
        assert 'GeneratorType that is not fully supported and may block the main thread' in str(warnings_list[0].message)

async def test_sync_command_generator_multiple_yielding_response():
    manager = CommandsManager()

    with warnings.catch_warnings(record = True) as warnings_list:
        @manager.new('start timer')
        def start_timer() -> Generator[Response, None, None]:
            yield Response(text = 'Timer started')
            yield Response(text = 'Timer 50% done')
            yield Response(text = 'Timer finished')

        expected = ['Timer started', 'Timer 50% done', 'Timer finished']
        for response in await start_timer(): # TODO: make generator async generator and use async for
            assert response.text == expected.pop(0)

        assert len(warnings_list) == 1
        assert issubclass(warnings_list[0].category, UserWarning)
        assert 'GeneratorType that is not fully supported and may block the main thread' in str(warnings_list[0].message)

async def test_exception_in_command():
    manager = CommandsManager()

    @manager.new('turn off the light')
    def lights_off() -> Response:
        raise Exception('smart bulb not responding')

    # with pytest.raises(Exception, match = 'smart bulb not responding'):
    #     await lights_off()

    assert (await lights_off()).status == ResponseStatus.error
