from __future__ import annotations

import logging
from abc import ABC
from dataclasses import dataclass
from typing import TYPE_CHECKING

from stark.core.command import Command
from stark.core.parsing import RecognizedEntity
from stark.core.types.object import Object

from .commands_manager import SearchResult

if TYPE_CHECKING:
    from stark.core.commands_context import CommandsContext


@dataclass
class CommandsContextLayer:
    commands: list[Command]
    parameters: dict[str, Object]


logger = logging.getLogger(__name__)


class CommandsContextProcessor(ABC):
    """
    Abstract base class for processors in the CommandsContext pipeline.

    Use cases:
    - Override `process` for processors that need to view or operate on the entire context queue at once.
      Example: NER markup for the string or AI-powered command search that considers all available contexts and commands in a single shot.
    - Override `process_context` for processors that operate on each context layer individually.
      Example: Classic pattern-based search.

    In most cases you should only override/implement one.

    The default implementation of `process` loops through the context queue, calling `process_context` for each layer.
    If any layer returns non-empty results, processing stops and returns those results along with the number of contexts popped.
    If all layers return empty results, all contexts are popped and an empty result list is returned.
    """

    async def process_string(
        self, string: str, context: CommandsContext, recognized_entities: list[RecognizedEntity]
    ) -> tuple[list[SearchResult], int]:
        """
        Processes the entire context queue.
        Returns a tuple: (results, pops)
          - results: list of SearchResult objects found (may be empty)
          - pops: number of context layers to pop after processing (0 if found a command in the current context)

        Default behavior: loop through context_queue, calling process_context for each.
        Stops at the first non-empty result and returns (results, pops).
        If all contexts return empty, returns ([], len(context_queue)). If no results, pop amount doesn't matter.

        If don't implement a command search (for example, implementing some type of pre-processing), return ([], 0)
        """
        pops = 0
        for layer in context.context_queue:
            logger.debug(f"Command search processing context {layer=} with {recognized_entities=}")
            results = await self.process_context_layer(
                string,
                context,
                layer,
                recognized_entities,
            )
            if results:
                return results, pops
            pops += 1
        return [], pops

    async def process_context_layer(
        self,
        string: str,
        context: CommandsContext,
        context_layer: CommandsContextLayer,
        recognized_entities: list[RecognizedEntity],
    ) -> list[SearchResult]:
        """
        Processes a single context layer.
        Returns a list of SearchResult objects (may be empty).

        Use case: Implement classic command search or other per-context logic.
        If results are empty, the context will be popped by the caller.
        """
        ...
