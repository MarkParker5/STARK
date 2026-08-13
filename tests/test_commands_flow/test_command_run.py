import anyio

from stark.core import Response
from stark.core.types import NLWord


async def test_command_flow_optional_parameter(commands_context_flow, autojump_clock):
    async with commands_context_flow() as (manager, context, context_delegate):
        # @manager.new('lorem ?hello ?$name:NLWord? dolor')
        @manager.new("lorem( hello $name:NLWord)? dolor")
        async def lorem_dolor(name: NLWord | None = None):
            return Response("Lorem!" + (name.value if name else ""))

        await context.process_string("lorem dolor")
        await anyio.sleep(5)
        assert len(context_delegate.responses) == 1
        assert context_delegate.responses[0].text == "Lorem!"

        await context.process_string("lorem hello ipsum dolor")
        await anyio.sleep(5)
        assert len(context_delegate.responses) == 2
        assert context_delegate.responses[1].text == "Lorem!ipsum"
