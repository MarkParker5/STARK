import warnings

import anyio

from stark.core import Response


async def test_commands_context_handle_async_generator(commands_context_flow, autojump_clock):
    async with commands_context_flow() as (manager, context, context_delegate):

        @manager.new("start timer")
        async def start_timer():
            await anyio.sleep(2)
            yield Response("Timer update 0")
            await anyio.sleep(2)
            yield Response("Timer update 1")
            await anyio.sleep(2)
            yield Response("Timer update 2")
            await anyio.sleep(2)
            yield Response("Timer update 3")
            await anyio.sleep(2)
            yield Response("Timer update 4")
            # return is not allowed in generators (functions with yield)

        await context.process_string("start timer")

        last_count = 0
        while last_count < 5:
            await anyio.sleep(1)
            if last_count == len(context_delegate.responses):
                continue
            assert len(context_delegate.responses) == last_count + 1
            last_count += 1
            assert context_delegate.responses[last_count - 1].text == f"Timer update {last_count - 1}"

        assert len(context_delegate.responses) == 5
        assert [r.text for r in context_delegate.responses] == [f"Timer update {i}" for i in range(5)]


async def test_commands_context_handle_sync_generator(commands_context_flow, autojump_clock):
    async with commands_context_flow() as (manager, context, context_delegate):

        @manager.new("start timer")
        def start_timer():
            yield Response("Timer update 0")
            yield Response("Timer update 1")
            yield Response("Timer update 2")
            yield Response("Timer update 3")
            yield Response("Timer update 4")
            # return is not allowed in generators (functions with yield)

        with warnings.catch_warnings(record=True) as warnings_list:
            await context.process_string("start timer")
            await anyio.sleep(1)

        assert len(warnings_list) == 2
        for warning in warnings_list:
            assert issubclass(warning.category, UserWarning)
            assert "GeneratorType that is not fully supported and may block the main thread" in str(warning.message)

        assert len(context_delegate.responses) == 5
        assert [r.text for r in context_delegate.responses] == [f"Timer update {i}" for i in range(5)]
