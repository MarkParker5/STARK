"""The Object/Word/String → NLObject/NLWord/NLString rename must stay backward-compatible."""

import warnings

import pytest

from stark.core.parsing import PatternParser
from stark.core.types import NLObject, NLString, NLWord


@pytest.mark.parametrize(
    ("old_name", "new_type"),
    [("Object", NLObject), ("Word", NLWord), ("String", NLString)],
)
def test_python_alias_maps_and_warns(old_name, new_type):
    import stark.core.types as types

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        obj = getattr(types, old_name)
    assert obj is new_type
    assert any(issubclass(w.category, DeprecationWarning) for w in caught)


def test_unknown_attribute_still_raises():
    import stark.core.types as types

    missing = "DefinitelyNotAType"
    with pytest.raises(AttributeError):
        getattr(types, missing)


async def test_old_dsl_names_still_parse():
    """Patterns written with the old `$x:Word` / `$x:String` names keep resolving."""
    pp = PatternParser()
    for old, new in (("Word", "NLWord"), ("String", "NLString")):
        assert pp.parameter_types_by_name[old] is pp.parameter_types_by_name[new]

    result = await pp.parse_object(NLWord, "hello")
    assert result.obj.value == "hello"
