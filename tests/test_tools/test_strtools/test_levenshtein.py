import pytest

from stark.tools import levenshtein
from stark.tools.levenshtein import SIMPLEPHONE_PROXIMITY_GRAPH


@pytest.mark.parametrize(
    "a,b,expected", # length, distance
    [
        ("", "", (0, 0)),
        ("a", "", (0, 1)),
        ("", "a", (0, 1)),
        ("a", "a", (1, 0)),
        ("a", "b", (1, 1)),
        ("ab", "ab", (2, 0)),
        ("ab", "ba", (2, 2)),
        ("abc", "yabcx", (5, 2)),
        ("yabcx", "abc", (3, 2)),
        ("sitting", "kitten", (6, 3)),
        ("kitten", "sitting", (7, 3)),
        ("flaw", "lawn", (4, 2)),
        ("elephant", "relevant", (8, 3)),
        ("relevant", "elephant", (8, 3)),
        ("saturday", "sunday", (6, 3)),
        ("sunday", "saturday", (8, 3)),
    ]
)
def test_levenshtein_distance_basic(a: str, b: str, expected: tuple[int, int]) -> None:
    assert levenshtein.levenshtein_distance(a, b) == expected

@pytest.mark.parametrize(
    "a,b,proximity_graph,expected",
    [
        ("ab", "ba", SIMPLEPHONE_PROXIMITY_GRAPH, (2, 1.25)),
        ("a", "w", SIMPLEPHONE_PROXIMITY_GRAPH, (1, 0.25)),
        ("w", "f", SIMPLEPHONE_PROXIMITY_GRAPH, (1, 0.5)),
    ]
)
def test_levenshtein_distance__proximity(a: str, b: str, proximity_graph, expected: tuple[float, int]) -> None:
    assert levenshtein.levenshtein_distance(a, b, proximity_graph=proximity_graph) == expected

@pytest.mark.parametrize(
    "a,b,expected",
    [
        ("lnknpk", "ln kn pk", (6, 0)),
        ("lnknpk", "ln kn pk", (6, 0)),
        ("ln kn pk", "lnknpk", (8, 0)),
        ("lnk npk", "lnknpk", (7, 0)),
    ]
)
def test_levenshtein_distance__skip_spaces(a: str, b: str, expected: tuple[int, int]) -> None:
    assert levenshtein.levenshtein_distance(a, b, proximity_graph={
        ' ': {'-': 0}, # space removed from s1
        '-': {' ': 0} # space inserted in s1
    }) == expected

@pytest.mark.parametrize(
    "a,b,expected",
    [
        # full match catched early
        ("lnknpk", "ln kn pk", (8, 0)),
        ("lnknpk", "ln kn pk", (8, 0)),
        ("lnk npk", "lnknpk", (6, 0)),
        ("ln kn pk", "lnknpk", (6, 0)),
        # DP table case
        ("lnknpk", "l n k n p k sit amet", (11, 0)),
        ("l n k n p k", "lnknpk sit amet", (6, 0)),
    ]
)
def test_levenshtein_distance__skip_spaces__square(a: str, b: str, expected: tuple[int, int]) -> None:
    assert levenshtein.levenshtein_distance(a, b, narrow=True, proximity_graph={
        ' ': {'-': 0}, # space removed from s1
        '-': {' ': 0} # space inserted in s1
    }) == expected

# TODO: def test_levenshtein_distance__square
# TODO: def test_levenshtein_distance__max_distance
# TODO: def test_levenshtein_similarity
# TODO: def test_levenshtein_match

@pytest.mark.parametrize(
    "query,string,min_similarity,expected",
    [
        # Empty query
        ("", "abc", 0.5, []),
        # Empty string
        ("abc", "", 0.5, []),
        # Exact middle match
        ("cat", "the cat sat", 0.0, ["cat"]),
        # Fuzzy middle match
        ("cat", "the bat sat", 0.60, ["bat", "sat"]),
        # bca and bcat satisfy threshold, but cat is a better match
        ("cat", "the bcat dog", 0.50, ["cat"]),
        # No match if min similarity is too high
        ("cat", "the bat sat", 1.0, []),
        # Easy case
        ("lnknpk", "lorem ispum lnknpk sit amet", 1, ["lnknpk"]),
        # Query without spaces, sentence with spaces
        ("lnknpk", "lorem ispum ln kn pk sit amet", 1, ["ln kn pk"]),
        # Query with spaces, sentence without
        ("ln kn pk", "lorem ispum lnknpk sit amet", 1, ["lnknpk"]),
        # Query and sentence both with spaces
        ("ln kn pk", "lorem ispum ln kn pk sit amet", 1, ["ln kn pk"]),
        # Multiword substring, multiple matches in a long sentence
        ("lnknpk", "lorem ispum ln kn pk sit amet lnk npk foo bar baz", 1, ["ln kn pk", "lnk npk"]),
        # Empty query
        ("", "hello", 0.5, []),
        # Empty string
        ("hello", "", 0.5, []),
        # Exact match
        ("hello", "hello", 0.5, ["hello"]),
        # No match
        ("hello", "world", 0.5, []),
        # Full similarity required
        ("hello", "hellw", 1, []),
        # No similarity - useless edge case
        ("hello", "world", 0, ["world"]),
    ]
)
def test_levenshtein_substrings_search_cases(query, string, min_similarity, expected):
    result = list(levenshtein.levenshtein_substrings_search(query, string, min_similarity, proximity_graph={
                ' ': {'-': 0}, # space removed from s1
                '-': {' ': 0} # space inserted in s1
            }))
    assert result == expected
