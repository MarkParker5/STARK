import pytest

from stark.tools import strtools


@pytest.mark.parametrize(
    "s,sep,expected",
    [
        ("foo bar baz", " ", [(0, 3), (4, 7), (8, 11)]),
        ("a,b,c", ",", [(0, 1), (2, 3), (4, 5)]),
        ("", " ", []),
        ("   ", " ", []),
        ("foo", " ", [(0, 3)]),
    ],
)
def test_split_indices_param(s: str, sep: str, expected: list[tuple[int, int]]):
    result = list(strtools.split_indices(s, sep=sep))
    assert result == expected


def test_find_substring_in_words_map_basic():
    words = ["foo", "bar", "baz"]
    substr = "bar"
    result = strtools.find_substring_in_words_map(substr, words)
    assert result == [[1]]


def test_find_substring_in_words_map_across_words():
    words = ["foo", "bar", "baz"]
    substr = "barbaz"
    result = strtools.find_substring_in_words_map(substr, words)
    assert result == [[1, 2]]


def test_find_substring_in_words_map_no_match():
    words = ["foo", "bar", "baz"]
    substr = "qux"
    result = strtools.find_substring_in_words_map(substr, words)
    assert result == []


@pytest.mark.parametrize(
    "s1,s2,expected",
    [
        ("foobar", "barbaz", "bar"),
        ("hello", "loworld", "lo"),
        ("abc", "xyz", ""),
        ("abc", "bc", "bc"),
        ("abc", "c", "c"),
        ("abc", "abc", "abc"),
        ("", "abc", ""),
        ("abc", "", ""),
    ],
)
def test_endswith_startof_param(s1: str, s2: str, expected: str):
    assert strtools.endswith_startof(s1, s2) == expected
