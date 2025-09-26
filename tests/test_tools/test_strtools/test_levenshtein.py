import pytest

from stark.tools import levenshtein


@pytest.mark.parametrize(
    "a,b,expected",
    [
        ("kitten", "sitting", 3),
        ("flaw", "lawn", 2),
        ("", "abc", 3),
        ("abc", "", 3),
        ("abc", "abc", 0),
        ("", "", 0),
        ("a", "a", 0),
        ("a", "b", 1),
    ]
)
def test_levenshtein_distance_param(a: str, b: str, expected: int) -> None:
    assert levenshtein.levenshtein_distance(a, b) == expected

@pytest.mark.parametrize(
    "a,b,expected",
    [
        ("abc", "abc", 1.0),
        ("abc", "ab", pytest.approx(1.0 - 1/3)),
        ("kitten", "sitting", pytest.approx(1.0 - 3/7)),
        ("", "abc", 0.0),
        ("abc", "", 0.0),
    ]
)
def test_levenshtein_similarity_param(a: str, b: str, expected: float) -> None:
    assert levenshtein.levenshtein_similarity(a, b) == expected

@pytest.mark.parametrize(
    "query,string,threshold,expected,comment",
    [
        # Exact match
        ("cat", "the cat sat", 0.0, {"cat"}, "Exact match"),
        # Fuzzy match
        ("cat", "the bat sat", 0.34, {"bat", "sat"}, "Fuzzy match"),
        # No match if threshold too low
        ("cat", "the bat sat", 0.0, set(), "No match if threshold too low"),
        # Multiword substring, multiple matches in a long sentence
        ("lnknpk", "lorem ispum ln kn pk sit amet lnk npk foo bar baz", 0, {"ln kn pk", "lnk npk"}, "Multiword, multiple matches"),
        # Query without spaces, sentence with spaces
        ("lnknpk", "lorem ispum ln kn pk sit amet", 0, {"ln kn pk"}, "Query without spaces, sentence with spaces"),
        # Query and sentence both with spaces
        ("ln kn pk", "lorem ispum ln kn pk sit amet", 0, {"ln kn pk"}, "Query and sentence both with spaces"),
        # Easy case
        ("lnknpk", "lorem ispum lnknpk sit amet", 0, {"lnknpk"}, "Easy case"),
        # Query with spaces, sentence without
        ("ln kn pk", "lorem ispum lnknpk sit amet", 0, {"lnknpk"}, "Query with spaces, sentence without"),
        # Empty query
        ("", "hello", 0.5, set(), "Empty query"),
        # Empty string
        ("hello", "", 0.5, set(), "Empty string"),
        # Exact match
        ("hello", "hello", 0.5, {"hello"}, "Exact match"),
        # No match
        ("hello", "world", 0.5, set(), "No match"),
        # Zero threshold
        ("hello", "world", 0, set(), "Zero threshold"),
        # One threshold
        ("hello", "world", 1, {"world"}, "One threshold"),
        # Debug cases
        ("AWATAAA", "LNKN PK", 0, set(), "Debug case 1"),
        ("ANSTKRM", "LNKN PK", 0, set(), "Debug case 2"),
        # Should skip leading spaces and match substrings across spaces
        ("bar", "foo bar baz", 0.0, {"bar"}, "Skip leading spaces, match substrings across spaces"),
        # Empty query and string
        ("", "abc", 0.5, set(), "Empty query"),
        ("abc", "", 0.5, set(), "Empty string"),
    ]
)
def test_levenshtein_substrings_search_cases(query, string, threshold, expected, comment):
    result = set(levenshtein.levenshtein_substrings_search(query, string, threshold))
    if expected:
        assert result & expected, f"{comment}: expected intersection with {expected}, got {result}"
    else:
        assert result == expected, f"{comment}: expected {expected}, got {result}"
