import pytest

from stark.tools import levenshtein
from stark.tools.levenshtein import SIMPLEPHONE_PROXIMITY_GRAPH


@pytest.mark.parametrize(
    "a,b,expected",
    [
        ("", "", (0, 0)),
        ("a", "", (1, 0)),
        ("", "a", (1, 0)),
        ("a", "a", (0, 1)),
        ("a", "b", (1, 1)),
        ("ab", "ab", (0, 2)),
        ("ab", "ba", (2, 2)),
        ("abc", "yabcx", (2, 5)),
        ("yabcx", "abc", (2, 3)),
        ("sitting", "kitten", (3, 6)),
        ("kitten", "sitting", (3, 7)),
        ("flaw", "lawn", (2, 4)),
        ("elephant", "relevant", (3, 8)),
        ("relevant", "elephant", (3, 8)),
        ("saturday", "sunday", (3, 6)),
        ("sunday", "saturday", (3, 8)),
    ]
)
def test_levenshtein_distance_basic(a: str, b: str, expected: tuple[int, int]) -> None:
    assert levenshtein.levenshtein_distance(a, b) == expected

@pytest.mark.parametrize(
    "a,b,proximity_graph,expected",
    [
        ("ab", "ba", SIMPLEPHONE_PROXIMITY_GRAPH, (1.25, 2)),
        ("a", "w", SIMPLEPHONE_PROXIMITY_GRAPH, (0.25, 1)),
        ("w", "f", SIMPLEPHONE_PROXIMITY_GRAPH, (0.5, 1)),
    ]
)
def test_levenshtein_distance__proximity(a: str, b: str, proximity_graph, expected: tuple[float, int]) -> None:
    assert levenshtein.levenshtein_distance(a, b, proximity_graph=proximity_graph) == expected

@pytest.mark.parametrize(
    "a,b,expected",
    [
        ("lnknpk", "ln kn pk", (0, 6)),
        ("lnknpk", "ln kn pk", (0, 6)),
        ("ln kn pk", "lnknpk", (0, 8)),
        ("lnk npk", "lnknpk", (0, 7))
    ]
)
def test_levenshtein_distance__skip_spaces(a: str, b: str, expected: tuple[int, int]) -> None:
    assert levenshtein.levenshtein_distance(a, b, skip_spaces=True) == expected

@pytest.mark.parametrize(
    "a,b,expected",
    [
        # full match catched early
        ("lnknpk", "ln kn pk", (0, 8)),
        ("lnknpk", "ln kn pk", (0, 8)),
        ("lnk npk", "lnknpk", (0, 6)),
        ("ln kn pk", "lnknpk", (0, 6)),
        # DP table case
        ("lnknpk", "l n k n p k sit amet", (0, 11)),
        ("l n k n p k", "lnknpk sit amet", (0, 6)),
    ]
)
def test_levenshtein_distance__skip_spaces__square(a: str, b: str, expected: tuple[int, int]) -> None:
    assert levenshtein.levenshtein_distance(a, b, skip_spaces=True, square=True) == expected

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
    result = list(levenshtein.levenshtein_substrings_search(query, string, min_similarity, skip_spaces=True))
    assert result == expected
