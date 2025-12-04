from __future__ import annotations

import logging
import subprocess
import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING, override

from stark.core.command import Command
from stark.core.commands_context_processor import CommandsContextProcessor
from stark.core.commands_manager import SearchResult
from stark.core.parsing import ObjectType, RecognizedEntity
from stark.core.types.location import Location
from stark.core.types.object import Object

if TYPE_CHECKING:
    from stark.core.commands_context import CommandsContext


@dataclass
class CommandsContextLayer:
    commands: list[Command]
    parameters: dict[str, Object]


logger = logging.getLogger(__name__)


class SpacyNERProcessor(CommandsContextProcessor):
    def __init__(
        self,
        lang_models: dict[str, str],
        label_types: dict[str, ObjectType | None] = {
            "CARDINAL": None,
            "DATE": None,
            "EVENT": None,
            "FAC": None,
            "GPE": Location,
            "LANGUAGE": None,
            "LAW": None,
            "LOC": Location,
            "MONEY": None,
            "NORP": None,
            "ORDINAL": None,
            "ORG": None,
            "PERCENT": None,
            "PERSON": None,
            "PRODUCT": None,
            "QUANTITY": None,
            "TIME": None,
            "WORK_OF_ART": None,
            "default": None,
        },
    ):
        """
        Find lang model names at https://spacy.io/usage/models#languages e.g. {"en": "en_core_web_sm"}. Installation is done automatically on the first run.
        """
        import spacy

        # lang_models.update({"xx": "xx"}) TODO: implement multilang

        self.nlps: dict[str, spacy.Language] = {}
        for lang, model in lang_models.items():
            try:
                self.nlps[lang] = spacy.load(model)
            except OSError:
                logger.warning(f"Model '{model}' not found for language '{lang}'")
                self._install_model(model)
                self.nlps[lang] = spacy.load(model)

        self.label_types = label_types

    # CommandsContextProcessor Impl

    @override
    async def process_string(
        self, string: str, context: CommandsContext, recognized_entities: list[RecognizedEntity]
    ) -> tuple[list[SearchResult], int]:
        lang = "en"  # TODO: pass lang, consider implementing multilang
        doc = self.nlps[lang](string)
        for entity in doc.ents:
            entity_type = self.label_types.get(entity.label_) or self.label_types.get("default")
            logger.debug(f"Found entity '{entity.text}' with label '{entity.label_}'. The corresponding entity type is {entity_type}.")
            if not entity_type:
                continue
            recognized_entities.append(RecognizedEntity(entity.text, entity_type))  # Span(entity.start, entity.end)
        return [], 0

    # Private

    def _install_model(self, model: str):
        logger.info(f"Installing model {model}...")

        proc = subprocess.Popen([sys.executable, "-m", "spacy", "download", model], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in proc.stdout or []:
            print(line, end="")
        proc.wait()

        if proc.returncode == 0:
            logger.info(f"Model {model} installed successfully.")
        else:
            logger.error(f"Failed to install model {model}. Return code: {proc.returncode}")
