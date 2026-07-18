import anyio

from stark.core import AsyncResponseHandler, Response
from stark.general.localisation.language_code import LanguageCode


async def test_commands_context_inject_dependencies(commands_context_flow, autojump_clock):
    async with commands_context_flow() as (manager, context, context_delegate):

        @manager.new("turn off the light")
        async def lights_off(handler: AsyncResponseHandler) -> Response:
            return Response("Lights off!")

        @manager.new("good night")
        async def good_night(inject_dependencies):
            return await inject_dependencies(lights_off)()

        await context.process_string("good night")
        await anyio.sleep(1)

        assert len(context_delegate.responses) == 1
        assert context_delegate.responses[0].text == "Lights off!"


async def test_language_code_injected_from_match(commands_context_flow, autojump_clock):
    from stark.general.localisation import LocaleString

    async with commands_context_flow() as (manager, context, context_delegate):

        @manager.new("hello")
        async def hello(lang: LanguageCode) -> Response:
            return Response(f"lang={lang}")

        await context.process_string(LocaleString("hello", "en"))
        await anyio.sleep(1)

        assert len(context_delegate.responses) == 1
        assert context_delegate.responses[0].text == "lang=en"


async def test_language_code_injected_any_parameter_name(commands_context_flow, autojump_clock):
    from stark.general.localisation import LocaleString

    async with commands_context_flow() as (manager, context, context_delegate):

        @manager.new("hello")
        async def hello(language: LanguageCode) -> Response:
            return Response(f"language={language}")

        await context.process_string(LocaleString("hello", "fr"))
        await anyio.sleep(1)

        assert len(context_delegate.responses) == 1
        assert context_delegate.responses[0].text == "language=fr"
