import pytest

from stark.tools.dictionary.dictionary import Dictionary, LookupMode, NameEntry
from stark.tools.dictionary.storage.storage_memory import DictionaryStorageMemory


@pytest.fixture
def dictionary() -> Dictionary:
    return Dictionary(storage=DictionaryStorageMemory())

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

    lang, name = name.split(':')
    dictionary.write_one(lang, name, metadata=data)

    lang, lookup = lookup.split(':')
    matches = dictionary.lookup(lookup, lang)

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
        matches = dictionary.lookup(entry.name, entry.language_code)
        assert matches
        assert matches[0].metadata["meta"] == entry.metadata["meta"]
    dictionary.clear()
    for entry in data:
        assert dictionary.lookup(entry.name, entry.language_code) == []

@pytest.mark.xfail(reason='TODO: update to use mode')
def test_lookup_fast_and_nonfast(dictionary: Dictionary):
    dictionary.write_one("en", "foo", {"x": 1})
    dictionary.write_one("en", "bar", {"x": 2})
    # Fast: should find exact simplephone match
    matches = dictionary.lookup("foo", "en", fast=True)
    assert matches and matches[0].name == "foo"
    # Non-fast: should fallback to contains search if no exact match
    matches = dictionary.lookup("fo", "en", fast=False)
    assert any(m.name == "foo" for m in matches)

def test_sentence_search(dictionary: Dictionary):
    # Add dictionary entries
    dictionary.write_one("en", "bar baz", {})
    sentence = "foo bar baz test ber buz foo"
    results = list(dictionary.sentence_search(sentence, "en", mode=LookupMode.FUZZY))
    assert results

    print(f'{results=}')

    found = []
    for result in results:
        # for match in result.items:
        found.append((result.span, result.item.name, result.item.simple_phonetic))
    # Should contain both multiword matches (update expected after seeing output)
    assert ((4, 11), "bar baz", "BRBZ") in found
    assert ((17, 24), "ber buz", "BRBZ") in found

# test_write_and_lookup_multiple_languages merged into test_write_one_and_lookup

def test_sorting_of_matches(dictionary: Dictionary):
    dictionary.write_one("en", "foo", {})
    dictionary.write_one("en", "food", {})
    matches = dictionary.lookup("foo", "en")
    # "foo" should be a better match than "food"
    assert matches
    assert matches[0].name == "foo"

def test_clear_removes_all(dictionary: Dictionary):
    dictionary.write_one("en", "foo", {})
    dictionary.clear()
    assert dictionary.lookup("foo", "en") == []

@pytest.mark.xfail(reason='TODO: update to use mode')
def test_lookup_fast_vs_nonfast_contain_case(dictionary: Dictionary):
    # Add a word that will only match as a substring in simplephone
    dictionary.write_one("en", "foobar", {})
    # "foo" should not match with fast=True (exact), but should match with fast=False (contains)
    fast_matches = dictionary.lookup("foo", "en", fast=True)
    nonfast_matches = dictionary.lookup("foo", "en", fast=False)
    assert fast_matches == []
    assert any(m.name == "foobar" for m in nonfast_matches)

@pytest.mark.parametrize(
    "entries,query,lang,expected",
    [
        # Basic suggestions (supported by current implementation)
        (
            [("hello", "en"), ("world", "en")],
            "hello world",
            "en",
            {("hello", "hello"), ("world", "world")},
        ),
        (
            [("hello", "en"), ("world", "en")],
            "hilo wart",
            "en",
            {("hilo", "hello"), ("wart", "world")},
        ),
        # Advanced multilingual suggestions (should fail if not supported)
        (
            [
                ("spotify", "en"),
                ("telegram", "en"),
                ("instagram", "en"),
                ("led zeppelin", "en"),
                ("imagine dragons", "en"),
                ("highway to hell", "en"),
                ("linkin park", "en"),
            ],
            "телеграм",
            "ru",
            {("телеграм", "telegram")},
        ),
        (
            [
                ("spotify", "en"),
                ("telegram", "en"),
                ("instagram", "en"),
                ("led zeppelin", "en"),
                ("imagine dragons", "en"),
                ("highway to hell", "en"),
                ("linkin park", "en"),
            ],
            "ледзеплин",
            "ru",
            {("ледзеплин", "led zeppelin")},
        ),
        (
            [
                ("spotify", "en"),
                ("telegram", "en"),
                ("instagram", "en"),
                ("led zeppelin", "en"),
                ("imagine dragons", "en"),
                ("highway to hell", "en"),
                ("linkin park", "en"),
            ],
            "имя джин драгонс",
            "ru",
            {("имя джин драгонс", "imagine dragons")},
        ),
        (
            [
                ("spotify", "en"),
                ("telegram", "en"),
                ("instagram", "en"),
                ("led zeppelin", "en"),
                ("imagine dragons", "en"),
                ("highway to hell", "en"),
                ("linkin park", "en"),
            ],
            "хайвей та хел",
            "ru",
            {("хайвей та хел", "highway to hell")},
        ),
        (
            [
                ("spotify", "en"),
                ("telegram", "en"),
                ("instagram", "en"),
                ("led zeppelin", "en"),
                ("imagine dragons", "en"),
                ("highway to hell", "en"),
                ("linkin park", "en"),
            ],
            "линкольн парк",
            "ru",
            {("линкольн парк", "linkin park")},
        ),
        (
            [
                ("spotify", "en"),
                ("telegram", "en"),
                ("instagram", "en"),
                ("led zeppelin", "en"),
                ("imagine dragons", "en"),
                ("highway to hell", "en"),
                ("linkin park", "en"),
            ],
            "спу ти фай",
            "ru",
            {("спу ти фай", "spotify")},
        ),
    ]
)
def test_lookup(dictionary: Dictionary, entries, query, lang, expected):
    from pprint import pprint
    pprint({"entries": entries, "query": query, "lang": lang, "expected": expected})
    # Add all keywords
    for name, language_code in entries:
        dictionary.write_one(language_code, name)
    # Simulate "get_string_suggestions" using lookup for each word in query
    suggestions = set()
    for word in query.split():
        matches = dictionary.lookup(word, lang)
        if matches:
            suggestions.add((word, matches[0].name))
    assert suggestions == expected

# TODO: stress test both memory and sql
