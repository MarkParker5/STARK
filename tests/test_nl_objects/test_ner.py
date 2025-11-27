from typing import cast

import pytest

from stark.core.commands_context import CommandsContext
from stark.core.parsing import RecognizedEntity
from stark.core.processors import SpacyNERProcessor
from stark.core.types.location import Location


@pytest.mark.parametrize(
    "input_text,expected_entities",
    [
        ("Let's meet in Washington DC next year.", [Location("Washington DC")]),
        ("How far is Lake Victoria?", [Location("Lake Victoria")]),
        ("buy tickets to new york and new orleans", [Location("new york"), Location("new orleans")]),
    ],
)
async def test_ner_layer(input_text, expected_entities):
    recognized_entities: list[RecognizedEntity] = []
    ner = SpacyNERProcessor(lang_models={"en": "en_core_web_sm"})
    await ner.process_string(input_text, cast(CommandsContext, None), recognized_entities)
    assert [e.type(e.substring) for e in recognized_entities] == expected_entities
