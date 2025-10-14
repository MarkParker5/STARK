import pytest

from stark.tools.dictionary.dictionary import Dictionary, LookupMode, NameEntry
from stark.tools.dictionary.models import Metadata
from stark.tools.dictionary.storage.storage_memory import DictionaryStorageMemory


@pytest.fixture
def dictionary() -> Dictionary:
    return Dictionary(storage=DictionaryStorageMemory())

def parse_lang(string: str) -> tuple[str, str]:
    lang = 'en'
    if ':' in string:
        lang, string = string.split(':', 1)
    return lang, string

@pytest.mark.parametrize(
    "name,lookup,data",
    [
        # English, Cyrillic, and German city name, all should match and return coords
        ("de:Nürnberg", "en:Nurnberg", {"coords": (49.45, 11.08)}),
        ("de:Nürnberg", "ru:Нюрнберг", {"coords": (49.45, 11.08)}),
        # English hello/hallo, Cyrillic hello/hallo
        ("en:hello", "de:hallo", {"coords": (49.45, 11.08)}),
        ("ru:хеллоу", "de:hallo", {"coords": (49.45, 11.08)}),
    ]
)
def test_write_one_and_lookup(dictionary: Dictionary, name: str, lookup: str, data):
    from pprint import pprint
    pprint({"name": name, "lookup": lookup, "data": data})
    # Use meta_key/meta_val for flexible assertion

    lang, name = parse_lang(name)
    dictionary.write_one(lang, name, metadata=data)

    lang, lookup = parse_lang(lookup)
    matches = list(dictionary.lookup(lookup, lang))

    assert matches
    assert matches[0].metadata == data

def test_write_all_and_clear(dictionary: Dictionary):
    data = [
        NameEntry(language_code="en", name="foo", metadata={"meta": 1}),
        NameEntry(language_code="en", name="bar", metadata={"meta": 2}),
        NameEntry(language_code="en", name="baz", metadata={"meta": 3}),
    ]
    dictionary.write_all(data)
    for entry in data:
        matches = list(dictionary.lookup(entry.name, entry.language_code))
        assert matches
        assert matches[0].metadata["meta"] == entry.metadata["meta"]
    dictionary.clear()
    for entry in data:
        assert list(dictionary.lookup(entry.name, entry.language_code)) == []

@pytest.mark.parametrize('entries,sentence,expected', [
    ([('lorem', {'id': 10})], 'foo lorem foo', [10]),
    ([('bar baz', {'id': 29}), ], 'foo ber baz foo', [29]),
    ([('lorem', {'id': 10})], 'foo lorem test lorem foo', [10, 10]),
    ([('imagine dragons', {'id': 1}),('linkin park', {'id': 2}),],
        'ru:включи имя джин драгонс или имейджин драгонс на колонке и потом добавь в очередь лин кин парк пожалуйста', [1, 1, 2]),
])
def test_sentence_search(dictionary: Dictionary, entries: list[tuple[str, Metadata]], sentence: str, expected: list[str]):
    for entry, data in entries:
        lang, name = parse_lang(entry)
        dictionary.write_one(lang, name, data)

    lang, sentence = parse_lang(sentence)

    results = list(dictionary.sentence_search(sentence, lang, mode=LookupMode.FUZZY))
    assert results, f'{expected} not found'

    found = [r.item.metadata['id'] for r in results]
    print(f'{found=}')
    assert found == expected

# test_write_and_lookup_multiple_languages merged into test_write_one_and_lookup

@pytest.mark.parametrize(
    "query,expected",
    [
        ("nurberg", ["nurberg", "nurburg"]),
        ("nurburg", ["nurburg", "nurberg"]),
    ]
)
def test_sorting_of_matches(dictionary: Dictionary, query: str, expected: list[str]):
    lang, name = parse_lang("en:nurberg")
    dictionary.write_one(lang, name, {})
    lang, name = parse_lang("en:nurburg")
    dictionary.write_one(lang, name, {})

    matches = list(dictionary.lookup_sorted(query, "en", mode=LookupMode.FUZZY))
    assert [match.name for match in matches] == expected

def test_clear_removes_all(dictionary: Dictionary):
    lang, name = parse_lang("en:foo")
    dictionary.write_one(lang, name, {})
    dictionary.clear()
    assert list(dictionary.lookup("foo", "en")) == []

@pytest.mark.parametrize(
    "entries,sentence,expected",
    [
        # Basic suggestions (supported by current implementation)
        (
            [('hello', {'id': 1}), ('world', {'id': 2})],
            'en:hello world',
            [1, 2],
        ),
        (
            [('hello', {'id': 1}), ('world', {'id': 2})],
            'en:hilo wart',
            [1, 2],
        ),

        # Advanced multilingual fuzzy matching
        (
            [
                ('spotify', {'id': 1}),
                ('telegram', {'id': 2}),
                ('instagram', {'id': 3}),
                ('led zeppelin', {'id': 4}),
                ('imagine dragons', {'id': 5}),
                ('highway to hell', {'id': 6}),
                ('linkin park', {'id': 7}),
            ],
            'ru:телеграм',
            [2],
        ),
        (
            [
                ('spotify', {'id': 1}),
                ('telegram', {'id': 2}),
                ('instagram', {'id': 3}),
                ('led zeppelin', {'id': 4}),
                ('imagine dragons', {'id': 5}),
                ('highway to hell', {'id': 6}),
                ('linkin park', {'id': 7}),
            ],
            'ru:ледзеплин',
            [4],
        ),
        (
            [
                ('spotify', {'id': 1}),
                ('telegram', {'id': 2}),
                ('instagram', {'id': 3}),
                ('led zeppelin', {'id': 4}),
                ('imagine dragons', {'id': 5}),
                ('highway to hell', {'id': 6}),
                ('linkin park', {'id': 7}),
            ],
            'ru:имя джин драгонс',
            [5],
        ),
        (
            [
                ('spotify', {'id': 1}),
                ('telegram', {'id': 2}),
                ('instagram', {'id': 3}),
                ('led zeppelin', {'id': 4}),
                ('imagine dragons', {'id': 5}),
                ('highway to hell', {'id': 6}),
                ('linkin park', {'id': 7}),
            ],
            'ru:хайвей та хел',
            [6],
        ),
        (
            [
                ('spotify', {'id': 1}),
                ('telegram', {'id': 2}),
                ('instagram', {'id': 3}),
                ('led zeppelin', {'id': 4}),
                ('imagine dragons', {'id': 5}),
                ('highway to hell', {'id': 6}),
                ('linkin park', {'id': 7}),
            ],
            'ru:линкольн парк',
            [7],
        ),
        (
            [
                ('spotify', {'id': 1}),
                ('telegram', {'id': 2}),
                ('instagram', {'id': 3}),
                ('led zeppelin', {'id': 4}),
                ('imagine dragons', {'id': 5}),
                ('highway to hell', {'id': 6}),
                ('linkin park', {'id': 7}),
            ],
            'ru:спу ти фай',
            [1],
        ),
    ]
)
def test_lookup(dictionary: Dictionary, entries: list[tuple[str, Metadata]], sentence: str, expected: list[int]):
    # Load entries into dictionary
    for entry, data in entries:
        lang, name = parse_lang(entry)
        dictionary.write_one(lang, name, data)

    lang, sentence = parse_lang(sentence)

    # Perform fuzzy search
    results = list(dictionary.sentence_search(sentence, lang, mode=LookupMode.FUZZY))
    assert results, f'{expected} not found'

    found = [r.item.metadata['id'] for r in results]
    print(f'{found=}')
    assert found == expected

@pytest.mark.parametrize(
    "entries,query,mode,expected_names",
    [
        # EXACT match only
        (["en:foo", "en:bar"], "foo", LookupMode.EXACT, ["foo"]),
        # CONTAINS match only
        (["en:foobar", "en:bar"], "foobar", LookupMode.CONTAINS, ["foobar", "bar"]),
        # FUZZY match only (typo)
        (["en:hello", "en:world"], "hellp", LookupMode.FUZZY, ["hello"]),
        # UNTIL_MATCH: EXACT wins
        (["en:foo", "en:foobar"], "foo", LookupMode.UNTIL_MATCH, ["foo"]),
        # UNTIL_MATCH: CONTAINS wins (no exact)
        (["en:foo", "en:bar"], "fo ba", LookupMode.UNTIL_MATCH, ["foo", "bar"]),
        # UNTIL_MATCH: FUZZY wins (no exact/contains)
        (["en:hello", "en:world"], "hellp", LookupMode.UNTIL_MATCH, ["hello"]),
        # UNTIL_MATCH: no matches
        (["en:foo", "en:bar"], "baz", LookupMode.UNTIL_MATCH, []),
    ]
)
def test_lookup_modes_and_until_match(dictionary: Dictionary, entries: list[str], query: str, mode: LookupMode, expected_names: list[str]):
    print(f"Testing '{query}' with mode {mode}")
    dictionary.clear()
    for entry in entries:
        lang, name = parse_lang(entry)
        dictionary.write_one(lang, name, {})
    results = list(dictionary.lookup(query, "en", mode=mode))
    assert [r.name for r in results] == expected_names

# TODO: test dictionary.sentence search with different modes

# TODO: stress test both memory and sql
