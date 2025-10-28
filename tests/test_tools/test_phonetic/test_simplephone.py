import pytest

from stark.tools.phonetic import simplephone


@pytest.mark.parametrize(
    "text,expected",
    [
        ("cat", "KT"),
        ("rough", "RF"),
        ("enough", "ANF"),
        ("trough", "TRF"),
        ("cough", "KF"),
        ("tough", "TF"),
        ("gnome", "NM"),
        ("dumb", "TM"),
        ("pharmacy", "FMSA"),
        ("bobby", "PPA"),
        ("shush", "SS"),
        ("buzz", "PS"),
        ("yellow", "YLA"),
        ("hello", "ALA"),
        ("whale", "WA"),
        ("wh3", None),
        ("y3", None),
        ("yarn", "YN"),
        ("hurry", "ARA"),
        ("lull", "LA"),
        ("rural", "RRA"),
        ("willow", "WLA"),
    ],
)
def test_simplephone_param(text: str, expected: str):
    result = simplephone.simplephone(text)
    assert result == expected
    result = simplephone.simplephone(text)
    if result != expected:
        print(f"simplephone.simplephone({text!r}) = {result!r} (expected {expected!r})")
    assert result == expected


@pytest.mark.parametrize(
    "text,expected,glue",
    [
        # no glue (default, more flexible)
        ("foo bar", "FAPA", ""),
        ("hello world", "ALAWT", ""),
        ("yellow submarine", "YLASPMRN", ""),
        ("", None, ""),
        ("   ", None, ""),
        ("foo   bar", "FAPA", ""),
        ("foo bar baz", "FAPAPS", ""),
        # space glue (word boundary preserved)
        ("foo bar", "FA PA", " "),
        ("hello world", "ALA WT", " "),
        ("yellow submarine", "YLA SPMRN", " "),
        ("", None, ""),
        ("   ", None, ""),
        ("foo   bar", "FA PA", " "),
        ("foo bar baz", "FA PA PS", " "),
    ],
)
def test_simplephone_multiword_sentences(text: str, expected: str | None, glue: str):
    assert simplephone.simplephone(text, glue=glue) == expected


def test_simplephone_empty_and_spaces():
    assert simplephone.simplephone("") is None
    assert simplephone.simplephone("   ") is None


def test_simplephone_word_empty():
    assert simplephone.simplephone_word("") is None
    assert simplephone.simplephone_word("   ") is None


def test_simplephone_word_only_vowels():
    assert simplephone.simplephone_word("aeiou") == "AA"
    assert simplephone.simplephone_word("e") is None


def test_simplephone_word_repeated_letters():
    assert simplephone.simplephone_word("bookkeeper") == "PKPA"
    assert simplephone.simplephone_word("committee") == "KMTA"
