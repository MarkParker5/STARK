import anyio
from stark.core.types import Word
from stark.core import Response


async def test_command_flow_optional_parameter(commands_context_flow, autojump_clock):
    async with commands_context_flow() as (manager, context, context_delegate):

        @manager.new('lorem( hello $var:Word)? dolor')
        async def foo(var: Word | None = None):
            return Response(text='Lorem!' + (var.value if var else ''))

        await context.process_string('lorem dolor')
        await anyio.sleep(5)
        assert len(context_delegate.responses) == 1
        assert context_delegate.responses[0].text == 'Lorem!'

        await context.process_string('lorem hello ipsum dolor')
        await anyio.sleep(5)
        assert len(context_delegate.responses) == 2
        assert context_delegate.responses[1].text == 'Lorem!ipsum'
