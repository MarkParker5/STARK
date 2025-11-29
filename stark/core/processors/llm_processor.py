from typing import Protocol

from typing_extensions import override

from stark.core.command import Response
from stark.core.commands_context import CommandsContext
from stark.core.commands_context_processor import CommandsContextLayer, CommandsContextProcessor
from stark.core.commands_manager import CommandsManager, SearchResult
from stark.core.parsing import RecognizedEntity
from stark.core.types.string import String

# class LLMPrompt(str, Enum):
#     CHAT = "You're ..."


class LLMProviderProtocol(Protocol): ...


class LLMProviderHttp(LLMProviderProtocol): ...


class LLMProviderFile(LLMProviderProtocol): ...


class LLMProcessor(CommandsContextProcessor):
    def __init__(self, llm_provider: LLMProviderProtocol):
        self.llm_provider = llm_provider

    # CommandsContextProcessor Implementation

    @override
    async def process_context_layer(
        self,
        string: str,
        context: CommandsContext,
        context_layer: CommandsContextLayer,
        recognized_entities: list[RecognizedEntity],
    ) -> list[SearchResult]: ...

    # Private

    async def _search_command(self, string: str, context_layer: CommandsContextLayer) -> list[SearchResult]: ...

    async def _recognize_parameters(self, string: str, search_result: SearchResult) -> list[RecognizedEntity]: ...


@CommandsManager().new("**", hidden=True)
async def run_llm_command(string: String, llm_provider: LLMProviderProtocol):
    """Fallback command to ask/run (a big) LLM as a last resort when no other command is suitable for the given input."""
    return Response.model_validate_strings(await llm_provider.chat(string))
