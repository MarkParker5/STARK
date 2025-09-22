import json
from typing import Any, AsyncGenerator, Callable, Type

from stark.core import CommandsManager, Response
from stark.core.types import Word
from stark.general.json_encoder import StarkJsonEncoder


async def test_command_json():
    manager = CommandsManager('TestManager')

    @manager.new('test pattern $word:Word')
    def test(var: str, word: Word, foo: int | None = None) -> Response:
        '''test command'''
        return Response(text=var)

    string = json.dumps(test, cls = StarkJsonEncoder)
    parsed = json.loads(string)

    assert parsed['name'] == 'TestManager.test'
    assert parsed['pattern']['origin'] == r'test pattern $word:Word'
    assert parsed['declaration'] == 'def test(var: str, word: Word, foo: int | None = None) -> Response'
    assert parsed['docstring'] == 'test command'

async def test_async_command_complicate_type_json():
    manager = CommandsManager('TestManager')

    @manager.new('async test')
    async def test2(
        some: AsyncGenerator[
            Callable[
                [Any], Type
            ],
            list[None]
        ]
    ):
        return Response()

    string = json.dumps(test2, cls = StarkJsonEncoder)
    parsed = json.loads(string)

    assert parsed['name'] == 'TestManager.test2'
    assert parsed['pattern']['origin'] == r'async test'
    assert parsed['declaration'] == 'async def test2(some: AsyncGenerator)' # TODO: improve AsyncGenerator to full type
    # assert parsed['declaration'] == 'async def test2(some: AsyncGenerator[Callable[[Any], Type], list[None], None])'
    assert parsed['docstring'] == ''

def test_manager_json():

    manager = CommandsManager('TestManager')

    @manager.new('')
    def test(): ...

    @manager.new('')
    def test2(): ...

    @manager.new('')
    def test3(): ...

    @manager.new('')
    def test4(): ...

    string = json.dumps(manager, cls = StarkJsonEncoder)
    parsed = json.loads(string)

    assert parsed['name'] == 'TestManager'
    assert {c['name'] for c in parsed['commands']} == {'TestManager.test', 'TestManager.test2', 'TestManager.test3', 'TestManager.test4',}
