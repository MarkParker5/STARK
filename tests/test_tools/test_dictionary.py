import pytest

from stark.tools.dictionary.dictionary import Dictionary, LookupMode, NameEntry
from stark.tools.dictionary.models import Metadata
from stark.tools.dictionary.storage.storage_memory import (
    DictionaryStorageMemory,
)
from stark.tools.dictionary.storage.storage_sqlite import (
    DictionaryStorageSQLite,
)


@pytest.fixture(params=["memory", "sqlite"])
def dictionary(request) -> Dictionary:
    print(f"Dictionary storage: {request.param}")
    if request.param == "memory":
        return Dictionary(storage=DictionaryStorageMemory())
    elif request.param == "sqlite":
        # Use in-memory SQLite for tests
        return Dictionary(storage=DictionaryStorageSQLite(":memory:"))
    raise ValueError(request.param)


def parse_lang(string: str) -> tuple[str, str]:
    lang = "en"
    if ":" in string:
        lang, string = string.split(":", 1)
    return lang, string


@pytest.mark.parametrize(
    "name,lookup,data",
    [
        # English, Cyrillic, and German city name, all should match and return coords
        ("de:Nürnberg", "en:Nurnberg", {"coords": [49.45, 11.08]}),
        ("de:Nürnberg", "ru:Нюрнберг", {"coords": [49.45, 11.08]}),
        # English hello/hallo, Cyrillic hello/hallo
        ("en:hello", "de:hallo", {"coords": [49.45, 11.08]}),
        ("ru:хеллоу", "de:hallo", {"coords": [49.45, 11.08]}),
    ],
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


@pytest.mark.parametrize(
    "entries,sentence,expected",
    [
        ([("lorem", {"id": 10})], "foo lorem foo", [10]),
        (
            [
                ("bar baz", {"id": 29}),
            ],
            "foo ber baz foo",
            [29],
        ),
        ([("lorem", {"id": 10})], "foo lorem test lorem foo", [10, 10]),
        (
            [
                ("imagine dragons", {"id": 1}),
                ("linkin park", {"id": 2}),
            ],
            "ru:включи имя джин драгонс или имейджин драгонс на колонке и потом добавь в очередь лин кин парк пожалуйста",
            [1, 1, 2],
        ),
    ],
)
def test_sentence_search(
    dictionary: Dictionary,
    entries: list[tuple[str, Metadata]],
    sentence: str,
    expected: list[str],
):
    for entry, data in entries:
        lang, name = parse_lang(entry)
        dictionary.write_one(lang, name, data)

    lang, sentence = parse_lang(sentence)

    results = list(dictionary.sentence_search(sentence, lang, mode=LookupMode.FUZZY))
    assert results, f"{expected} not found"

    found = [r.item.metadata["id"] for r in results]
    print(f"{found=}")
    assert found == expected


# test_write_and_lookup_multiple_languages merged into test_write_one_and_lookup


@pytest.mark.parametrize(
    "query,expected",
    [
        ("nurberg", ["nurberg", "nurburg"]),
        ("nurburg", ["nurburg", "nurberg"]),
    ],
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
            [("hello", {"id": 1}), ("world", {"id": 2})],
            "en:hello world",
            [1, 2],
        ),
        (
            [("hello", {"id": 1}), ("world", {"id": 2})],
            "en:hilo wart",
            [1, 2],
        ),
        # Advanced multilingual fuzzy matching
        (
            [
                ("spotify", {"id": 1}),
                ("telegram", {"id": 2}),
                ("instagram", {"id": 3}),
                ("led zeppelin", {"id": 4}),
                ("imagine dragons", {"id": 5}),
                ("highway to hell", {"id": 6}),
                ("linkin park", {"id": 7}),
            ],
            "ru:телеграм",
            [2],
        ),
        (
            [
                ("spotify", {"id": 1}),
                ("telegram", {"id": 2}),
                ("instagram", {"id": 3}),
                ("led zeppelin", {"id": 4}),
                ("imagine dragons", {"id": 5}),
                ("highway to hell", {"id": 6}),
                ("linkin park", {"id": 7}),
            ],
            "ru:ледзеплин",
            [4],
        ),
        (
            [
                ("spotify", {"id": 1}),
                ("telegram", {"id": 2}),
                ("instagram", {"id": 3}),
                ("led zeppelin", {"id": 4}),
                ("imagine dragons", {"id": 5}),
                ("highway to hell", {"id": 6}),
                ("linkin park", {"id": 7}),
            ],
            "ru:имя джин драгонс",
            [5],
        ),
        (
            [
                ("spotify", {"id": 1}),
                ("telegram", {"id": 2}),
                ("instagram", {"id": 3}),
                ("led zeppelin", {"id": 4}),
                ("imagine dragons", {"id": 5}),
                ("highway to hell", {"id": 6}),
                ("linkin park", {"id": 7}),
            ],
            "ru:хайвей та хел",
            [6],
        ),
        (
            [
                ("spotify", {"id": 1}),
                ("telegram", {"id": 2}),
                ("instagram", {"id": 3}),
                ("led zeppelin", {"id": 4}),
                ("imagine dragons", {"id": 5}),
                ("highway to hell", {"id": 6}),
                ("linkin park", {"id": 7}),
            ],
            "ru:линкольн парк",
            [7],
        ),
        (
            [
                ("spotify", {"id": 1}),
                ("telegram", {"id": 2}),
                ("instagram", {"id": 3}),
                ("led zeppelin", {"id": 4}),
                ("imagine dragons", {"id": 5}),
                ("highway to hell", {"id": 6}),
                ("linkin park", {"id": 7}),
            ],
            "ru:спу ти фай",
            [1],
        ),
    ],
)
def test_lookup(
    dictionary: Dictionary,
    entries: list[tuple[str, Metadata]],
    sentence: str,
    expected: list[int],
):
    # Load entries into dictionary
    for entry, data in entries:
        lang, name = parse_lang(entry)
        dictionary.write_one(lang, name, data)

    lang, sentence = parse_lang(sentence)

    # Perform fuzzy search
    results = list(dictionary.sentence_search(sentence, lang, mode=LookupMode.FUZZY))
    assert results, f"{expected} not found"

    found = [r.item.metadata["id"] for r in results]
    print(f"{found=}")
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
        # AUTO: EXACT wins
        (["en:foo", "en:foobar"], "foo", LookupMode.AUTO, ["foo"]),
        # AUTO: CONTAINS wins (no exact)
        (["en:foo", "en:bar"], "fo ba", LookupMode.AUTO, ["foo", "bar"]),
        # AUTO: FUZZY wins (no exact/contains)
        (["en:hello", "en:world"], "hellp", LookupMode.AUTO, ["hello"]),
        # AUTO: no matches
        (["en:foo", "en:bar"], "baz", LookupMode.AUTO, []),
    ],
)
def test_lookup_modes(
    dictionary: Dictionary,
    entries: list[str],
    query: str,
    mode: LookupMode,
    expected_names: list[str],
):
    print(f"Testing '{query}' with mode {mode}")
    dictionary.clear()
    for entry in entries:
        lang, name = parse_lang(entry)
        dictionary.write_one(lang, name, {})
    results = list(dictionary.lookup_sorted(query, "en", mode=mode))
    assert [r.name for r in results] == expected_names


@pytest.mark.parametrize(
    "entries,sentence,mode,expected_names",
    [
        # EXACT (single-word): Only matches if entry is exactly a word in the sentence
        (
            ["en:dragons", "en:linkin", "en:zeppelin"],
            "play dragons and linkin",
            LookupMode.EXACT,
            ["dragons", "linkin"],
        ),
        # EXACT (multi-word): Only matches if entry is exactly a word in the sentence
        (
            ["en:imagine dragons", "en:linkin park", "en:led zeppelin"],
            "play imagine dragons and linkin park",
            LookupMode.EXACT,
            ["imagine dragons", "linkin park"],
        ),
        # CONTAINS (single-word): Matches if entry is fully present inside the sentence
        (
            ["en:dragons", "en:linkin", "en:zeppelin"],
            "please play imagine dragons and then add linkin park to the queue",
            LookupMode.CONTAINS,
            ["dragons", "linkin"],
        ),
        # CONTAINS (multi-word): Matches if entry is fully present inside the sentence
        (
            ["en:imagine dragons", "en:linkin park", "en:led zeppelin"],
            "please play imagine dragons and then add linkin park to the queue",
            LookupMode.CONTAINS,
            ["imagine dragons", "linkin park"],
        ),
        # FUZZY: Matches phonetically similar entries (typos, transliterations)
        (
            ["en:imagine dragons", "en:linkin park", "en:led zeppelin"],
            "play имя джин драгонс и лин кин парк",
            LookupMode.FUZZY,
            ["imagine dragons", "linkin park"],
        ),
        # FUZZY: Typo tolerance
        (
            ["en:imagine dragons", "en:linkin park"],
            "play imagine dragns and linkin prk",
            LookupMode.FUZZY,
            ["imagine dragons", "linkin park"],
        ),
        # AUTO: Should return EXACT if present
        (
            ["en:imagine dragons", "en:linkin park", "en:led zeppelin"],
            "play imagine dragons and linkin park",
            LookupMode.AUTO,
            ["imagine dragons", "linkin park"],
        ),
        # AUTO: No EXACT, but CONTAINS present
        (
            ["en:imagine dragons", "en:linkin park"],
            "please play imagine dragons and add linkin park",
            LookupMode.AUTO,
            ["imagine dragons", "linkin park"],
        ),
        # AUTO: No EXACT/CONTAINS, FUZZY present
        (
            ["en:imagine dragons", "en:linkin park"],
            "play имя джин драгонс и лин кин парк",
            LookupMode.AUTO,
            ["imagine dragons", "linkin park"],
        ),
        # AUTO: No matches at all
        (
            ["en:imagine dragons", "en:linkin park"],
            "play something else",
            LookupMode.AUTO,
            [],
        ),
    ],
)
def test_sentence_search_modes(
    dictionary: Dictionary,
    entries: list[str],
    sentence: str,
    mode: LookupMode,
    expected_names: list[str],
):
    dictionary.clear()
    for entry in entries:
        lang, name = parse_lang(entry)
        dictionary.write_one(lang, name, {})
    results = list(dictionary.sentence_search_sorted(sentence, "en", mode=mode))
    found_names = [r.item.name for r in results]
    assert sorted(found_names) == sorted(expected_names)
