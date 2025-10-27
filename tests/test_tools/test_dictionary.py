import pytest

from stark.tools.dictionary.dictionary import (
    Dictionary,
    LookupField,
    LookupMode,
    NameEntry,
)
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
    "entries,query,mode,field,expected_names",
    [
        # PHONETIC (default) cases
        (["en:foo", "en:bar"], "foo", LookupMode.EXACT, LookupField.PHONETIC, ["foo"]),
        (
            ["en:foobar", "en:bar"],
            "foobar",
            LookupMode.CONTAINS,
            LookupField.PHONETIC,
            ["foobar", "bar"],
        ),
        (
            ["en:hello", "en:world"],
            "hellp",
            LookupMode.FUZZY,
            LookupField.PHONETIC,
            ["hello"],
        ),
        (
            ["en:foo", "en:foobar"],
            "foo",
            LookupMode.AUTO,
            LookupField.PHONETIC,
            ["foo"],
        ),
        (
            ["en:foo", "en:bar"],
            "fo ba",
            LookupMode.AUTO,
            LookupField.PHONETIC,
            ["foo", "bar"],
        ),
        (
            ["en:hello", "en:world"],
            "hellp",
            LookupMode.AUTO,
            LookupField.PHONETIC,
            ["hello"],
        ),
        (["en:foo", "en:bar"], "baz", LookupMode.AUTO, LookupField.PHONETIC, []),
        # NAME field cases (should behave the same for these examples)
        (["en:foo", "en:bar"], "foo", LookupMode.EXACT, LookupField.NAME, ["foo"]),
        (
            ["en:foobar", "en:bar"],
            "foobar",
            LookupMode.CONTAINS,
            LookupField.NAME,
            ["foobar", "bar"],
        ),
        (
            ["en:hello", "en:world"],
            "hellp",
            LookupMode.FUZZY,
            LookupField.NAME,
            [],
        ),
        (["en:foo", "en:foobar"], "foo", LookupMode.AUTO, LookupField.NAME, ["foo"]),
        (
            ["en:foo", "en:bar"],
            "fo ba",
            LookupMode.AUTO,
            LookupField.NAME,
            [],
        ),
        (
            ["en:hello", "en:world"],
            "hellp",
            LookupMode.AUTO,
            LookupField.NAME,
            [],
        ),
        (["en:foo", "en:bar"], "baz", LookupMode.AUTO, LookupField.NAME, []),
    ],
)
def test_lookup_modes(
    dictionary: Dictionary,
    entries: list[str],
    query: str,
    mode: LookupMode,
    field: LookupField,
    expected_names: list[str],
):
    print(f"Testing '{query}' with mode {mode} and field {field}")
    dictionary.clear()
    for entry in entries:
        lang, name = parse_lang(entry)
        dictionary.write_one(lang, name, {})
    results = list(dictionary.lookup_sorted(query, "en", mode=mode, field=field))
    assert [r.name for r in results] == expected_names


@pytest.mark.parametrize(
    "entries,sentence,mode,expected_names,field",
    [
        # PHONETIC (default) cases
        (
            ["en:dragons", "en:linkin", "en:zeppelin"],
            "play dragons and linkin",
            LookupMode.EXACT,
            ["dragons", "linkin"],
            LookupField.PHONETIC,
        ),
        (
            ["en:imagine dragons", "en:linkin park", "en:led zeppelin"],
            "play imagine dragons and linkin park",
            LookupMode.EXACT,
            ["imagine dragons", "linkin park"],
            LookupField.PHONETIC,
        ),
        (
            ["en:dragons", "en:linkin", "en:zeppelin"],
            "please play imagine dragons and then add linkin park to the queue",
            LookupMode.CONTAINS,
            ["dragons", "linkin"],
            LookupField.PHONETIC,
        ),
        (
            ["en:imagine dragons", "en:linkin park", "en:led zeppelin"],
            "please play imagine dragons and then add linkin park to the queue",
            LookupMode.CONTAINS,
            ["imagine dragons", "linkin park"],
            LookupField.PHONETIC,
        ),
        (
            ["en:imagine dragons", "en:linkin park", "en:led zeppelin"],
            "play имя джин драгонс и лин кин парк",
            LookupMode.FUZZY,
            ["imagine dragons", "linkin park"],
            LookupField.PHONETIC,
        ),
        (
            ["en:imagine dragons", "en:linkin park"],
            "play imagine dragns and linkin prk",
            LookupMode.FUZZY,
            ["imagine dragons", "linkin park"],
            LookupField.PHONETIC,
        ),
        (
            ["en:imagine dragons", "en:linkin park", "en:led zeppelin"],
            "play imagine dragons and linkin park",
            LookupMode.AUTO,
            ["imagine dragons", "linkin park"],
            LookupField.PHONETIC,
        ),
        (
            ["en:imagine dragons", "en:linkin park"],
            "please play imagine dragons and add linkin park",
            LookupMode.AUTO,
            ["imagine dragons", "linkin park"],
            LookupField.PHONETIC,
        ),
        (
            ["en:imagine dragons", "en:linkin park"],
            "play имя джин драгонс и лин кин парк",
            LookupMode.AUTO,
            ["imagine dragons", "linkin park"],
            LookupField.PHONETIC,
        ),
        (
            ["en:imagine dragons", "en:linkin park"],
            "play something else",
            LookupMode.AUTO,
            [],
            LookupField.PHONETIC,
        ),
        # NAME field cases (should behave the same for these examples)
        (
            ["en:dragons", "en:linkin", "en:zeppelin"],
            "play dragons and linkin",
            LookupMode.EXACT,
            ["dragons", "linkin"],
            LookupField.NAME,
        ),
        (
            ["en:imagine dragons", "en:linkin park", "en:led zeppelin"],
            "play imagine dragons and linkin park",
            LookupMode.EXACT,
            ["imagine dragons", "linkin park"],
            LookupField.NAME,
        ),
        (
            ["en:dragons", "en:linkin", "en:zeppelin"],
            "please play imagine dragons and then add linkin park to the queue",
            LookupMode.CONTAINS,
            ["dragons", "linkin"],
            LookupField.NAME,
        ),
        (
            ["en:imagine dragons", "en:linkin park", "en:led zeppelin"],
            "please play imagine dragons and then add linkin park to the queue",
            LookupMode.CONTAINS,
            ["imagine dragons", "linkin park"],
            LookupField.NAME,
        ),
        (
            ["en:imagine dragons", "en:linkin park"],
            "play imagine dragons and linkin park",
            LookupMode.FUZZY,
            ["imagine dragons", "linkin park"],
            LookupField.NAME,
        ),
        (
            ["en:imagine dragons", "en:linkin park"],
            "play imagine dragns and linkin prk",
            LookupMode.FUZZY,
            ["imagine dragons", "linkin park"],
            LookupField.NAME,
        ),
        (
            ["en:imagine dragons", "en:linkin park"],
            "play linkin park and imagine dragons",
            LookupMode.FUZZY,
            ["linkin park", "imagine dragons"],
            LookupField.NAME,
        ),
    ],
)
def test_sentence_search_modes(
    dictionary: Dictionary,
    entries: list[str],
    sentence: str,
    mode: LookupMode,
    expected_names: list[str],
    field: LookupField,
):
    dictionary.clear()
    for entry in entries:
        lang, name = parse_lang(entry)
        dictionary.write_one(lang, name, {})
    results = list(
        dictionary.sentence_search_sorted(sentence, "en", mode=mode, field=field)
    )
    found_names = [r.item.name for r in results]
    assert sorted(found_names) == sorted(expected_names)


@pytest.mark.parametrize(
    "field,expected",
    [
        (LookupField.NAME, ["Qatar"]),
        (LookupField.PHONETIC, ["Qatar", "guitar"]),
    ],
)
def test_lookupfield_name_vs_phonetic(dictionary, field, expected):
    dictionary.clear()
    dictionary.write_one("en", "Qatar", {"meta": 1})
    dictionary.write_one("en", "guitar", {"meta": 2})
    dictionary.write_one("en", "bar", {"meta": 3})

    results = list(dictionary.lookup("Qatar", "en", field=field))
    found_names = [r.name for r in results]
    assert len(found_names) == len(expected), (
        f"Expected {len(expected)} matches, but got {len(found_names)} "
        f"({', '.join(found_names)})"
    )
    assert sorted(found_names) == sorted(expected)
