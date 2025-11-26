import anyio

from stark.core import AsyncResponseHandler, Response


async def test_commands_context_inject_dependencies(commands_context_flow, autojump_clock):
    async with commands_context_flow() as (manager, context, context_delegate):

        @manager.new("foo")
        async def foo(handler: AsyncResponseHandler) -> Response:
            return Response(text="foo!")

        @manager.new("bar")
        async def bar(inject_dependencies):
            return await inject_dependencies(foo)()

        await context.process_string("bar")
        await anyio.sleep(1)

        assert len(context_delegate.responses) == 1
        assert context_delegate.responses[0].text == "foo!"
