import pytest

from stark.core.patterns.parsing import ParseError
from stark.tools.dictionary.dictionary import Dictionary
from stark.tools.dictionary.models import DictionaryItem
from stark.tools.dictionary.nl_dictionary_name import NLDictionaryName
from stark.tools.dictionary.storage.storage_memory import DictionaryStorageMemory


class NLCityName(NLDictionaryName):
    dictionary = Dictionary(storage=DictionaryStorageMemory())

@pytest.fixture(autouse=True)
def setup_dictionary():
    NLCityName.dictionary.clear()
    NLCityName.dictionary.write_one('de', 'Nürnberg', {'coords': (49.45, 11.08)})
    NLCityName.dictionary.write_one('en', 'London', {'coords': (51.51, -0.13)})
    NLCityName.dictionary.write_one('en', 'Paris', {'coords': (48.85, 2.35)})
    # NLCityName.dictionary.write_one('fr', 'Paris', {'coords': (48.85, 2.35)})

@pytest.mark.parametrize("query,expected_city, expected_coords", [
    ("Nurnberg", "Nurnberg", (49.45, 11.08)),
    ("London", "London", (51.51, -0.13)),
    ("Paris", "Paris", (48.85, 2.35)),
    ("Nernburg", "Nernburg", (49.45, 11.08)),
    ("No place like Landn", "Landn", (51.51, -0.13)),
    ("Notre Dame de Paris Musical", "Paris", (48.85, 2.35)),
])
async def test_nl_dictionary_name_lookup(query: str, expected_city: str, expected_coords: tuple[float, float]):
    assert expected_city in query # make sure test is not broken
    obj = NLCityName(value=[])
    substr = await obj.did_parse(query)
    assert obj.value
    assert isinstance(obj.value, DictionaryItem)
    assert obj.value.metadata["coords"] == expected_coords
    assert substr == expected_city

async def test_nl_dictionary_name_not_found():
    obj = NLCityName(value=[])
    with pytest.raises(ParseError):
        await obj.did_parse("notfound")
