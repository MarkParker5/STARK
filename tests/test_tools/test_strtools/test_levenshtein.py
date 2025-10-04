import pytest

from stark.tools import levenshtein
from stark.tools.levenshtein import SIMPLEPHONE_PROXIMITY_GRAPH, LevenshteinDistanceMode

SKIP_SPACES_GRAPH = {
    ' ': {'-': 0.0}, # space removed from s1
    '-': {' ': 0.0} # space inserted in s1
}

@pytest.mark.parametrize(
    "a,b,exp_span,exp_distance", # length, distance
    [
        # longer words + symetry test
        ("abc", "yabcx", (0, 5), 2),
        ("yabcx", "abc", (0, 5), 2),
        ("flaw", "lawn", (0, 4), 2),
        ("lawn", "flaw", (0, 4), 2),
        ("sitting", "kitten", (0, 7), 3),
        ("kitten", "sitting", (0, 7), 3),
        ("saturday", "sunday", (0, 8), 3),
        ("sunday", "saturday", (0, 8), 3),
        ("elephant", "relevant", (0, 8), 3),
        ("relevant", "elephant", (0, 8), 3),
    ]
)
def test_levenshtein_distance__long(a: str, b: str, exp_span: tuple[int, int], exp_distance: float) -> None:
    # NOTE: both nums are less by 1.0, the alg cuts the last letter for better substr match:
    # TODO: check which string is required to be complete and which is allowed to be cut
    span, distance = levenshtein.levenshtein_distance(a, b)
    errors = []
    if span != exp_span:
        errors.append(f'exp span {exp_span} != {span}')
    if distance != exp_distance:
        errors.append(f'exp distance {exp_distance} != {distance}')
    assert not errors, '\t' + '; '.join(errors)

@pytest.mark.parametrize(
    "a,b,exp_span,exp_distance",
    [
        ("abc", "abcyz", (0, 3), 0), # extra trailing - cut
        ("abcyz", "abc", (0, 3), 0),
        ("abc", "xxabcyz", (2, 5), 0), # extra both leading and trailing - cut
        ("xxabcyz", "abc", (2, 5), 0),
        ("flaw", "lawn", (0, 3), 1), # possible asymetrical result with same length words (probably due to unhandled extra leading chars)
        ("lawn", "flaw", (1, 4), 1),
        ("elephant", "relevant", (1, 8), 2),
        ("relevant", "elephant", (0, 8), 3),
        ("sitting", "kitten", (0, 6), 2), # different length gets swaped to make s1 no longer than s2, so different length is symmetric
        ("kitten", "sitting", (0, 6), 2),
        ("saturday", "sunday", (2, 8), 2),
        ("sunday", "saturday", (2, 8), 2),
    ]
)
def test_levenshtein_distance__substring(a: str, b: str, exp_span: tuple[int, int], exp_distance: float) -> None:
    # NOTE: both nums are less by 1.0, the alg cuts the last letter for better substr match:
    # TODO: check which string is required to be complete and which is allowed to be cut
    span, distance = levenshtein.levenshtein_distance(a, b, mode=LevenshteinDistanceMode.SUBSTRING)
    errors = []
    if span != exp_span:
        errors.append(f'exp span {exp_span} != {span}')
    if distance != exp_distance:
        errors.append(f'exp distance {exp_distance} != {distance}')
    assert not errors, '\t' + '; '.join(errors)

@pytest.mark.parametrize(
    "a,b,proximity_graph,exp_span,exp_distance",
    [
        ("ab", "ba", SIMPLEPHONE_PROXIMITY_GRAPH, (0, 2), 1.25),
        ("a", "w", SIMPLEPHONE_PROXIMITY_GRAPH, (0, 1), 0.25),
        ("w", "f", SIMPLEPHONE_PROXIMITY_GRAPH, (0, 1), 0.5),
    ]
)
def test_levenshtein_distance__proximity(a: str, b: str, proximity_graph, exp_span: tuple[int, int], exp_distance: float) -> None:
    span, distance = levenshtein.levenshtein_distance(a, b, proximity_graph=proximity_graph)
    errors = []
    if span != exp_span:
        errors.append(f'exp span {exp_span} != {span}')
    if distance != exp_distance:
        errors.append(f'exp distance {exp_distance} != {distance}')
    assert not errors, '\t' + '; '.join(errors)

@pytest.mark.parametrize(
    "a,b,exp_span,exp_distance",
    [
        ("lnknpk", "ln kn pk", (0, 8), 0),
        ("ln kn pk", "lnknpk", (0, 8), 0),
        ("lnk npk", "lnknpk", (0, 7), 0),
    ]
)
def test_levenshtein_distance__skip_spaces(a: str, b: str, exp_span: tuple[int, int], exp_distance: float) -> None:
    span, distance = levenshtein.levenshtein_distance(a, b, proximity_graph=SKIP_SPACES_GRAPH)
    errors = []
    if exp_span != span:
        errors.append(f'exp span {exp_span} != {span}')
    if exp_distance != distance:
        errors.append(f'exp distance {exp_distance} != {distance}')
    assert not errors, '\t' + '; '.join(errors)

@pytest.mark.parametrize(
    "a,b,exp_span,exp_distance",
    [
        # full match catched early
        ("lnknpk", "ln kn pk", (0, 8), 0),
        ("ln kn pk", "lnknpk", (0, 8), 0),
        ("lnk npk", "lnknpk", (0, 7), 0),
        # DP table case
        ("lnknpk", "l n k n p k sit amet", (0, 11), 0),
        ("l n k n p k", "lnknpk sit amet", (0, 6), 0),
        ("cat sat", "cat", (0, 3), 0),
        ("the cat sat", "cat", (4, 7), 0),
        ("abc cat def cat ghj cat klm", "cat", (4, 7), 0),
        # ("cat", "the cat sat", (4, 7), 0),
    ]
)
def test_levenshtein_distance__skip_spaces__substring(a: str, b: str, exp_span: tuple[int, int], exp_distance: float) -> None:
    span, distance = levenshtein.levenshtein_distance(a, b, mode=LevenshteinDistanceMode.SUBSTRING, proximity_graph=SKIP_SPACES_GRAPH)
    errors = []
    if exp_span != span:
        errors.append(f'exp span {exp_span} != {span}')
    if exp_distance != distance:
        errors.append(f'exp distance {exp_distance} != {distance}')
    assert not errors, '\t' + '; '.join(errors)

# @pytest.mark.parametrize(
#     "a,b,exp_span,exp_similarity",
#     [
#         # full match catched early
#         ("lnknpk", "ln kn pk", (0, 8), 1),
#         ("ln kn pk", "lnknpk", (0, 8), 1),
#         ("lnk npk", "lnknpk", (0, 7), 1),
#         # DP table case
#         ("lnknpk", "l n k n p k sit amet", (0, 11), 1),
#         ("l n k n p k", "lnknpk sit amet", (0, 6), 1),
#         ("the cat sat", "cat", (4, 7), 1),
#         ("cat", "the cat sat", (4, 7), 1),
#     ]
# )
# def test_levenshtein_similarity__skip_spaces__substring__no_tolerance(a: str, b: str, exp_span: tuple[int, int], exp_similarity: float) -> None:
#     span, similarity = levenshtein.levenshtein_similarity(a, b, min_similarity=1.0, mode=LevenshteinDistanceMode.SUBSTRING, proximity_graph=SKIP_SPACES_GRAPH)
#     errors = []
#     if exp_span != span:
#         errors.append(f'exp span {exp_span} != {span}')
#     if exp_similarity != similarity:
#         errors.append(f'exp similarity {exp_similarity} != {similarity}')
#     assert not errors, '\t' + '; '.join(errors)

# @pytest.mark.parametrize(
#     "a,b,exp_span,exp_match",
#     [
#         # full match catched early
#         ("lnknpk", "ln kn pk", (0, 8), True),
#         ("ln kn pk", "lnknpk", (0, 8), True),
#         ("lnk npk", "lnknpk", (0, 7), True),
#         # DP table case
#         ("lnknpk", "l n k n p k sit amet", (0, 11), True),
#         ("l n k n p k", "lnknpk sit amet", (0, 6), True),
#         ("the cat sat", "cat", (4, 7), True),
#         ("cat", "the cat sat", (4, 7), True),
#     ]
# )
# def test_levenshtein_match__skip_spaces__substring__no_tolerance(a: str, b: str, exp_span: tuple[int, int], exp_match: bool) -> None:
#     match, span = levenshtein.levenshtein_match(a, b, min_similarity=1.0, mode=LevenshteinDistanceMode.SUBSTRING, proximity_graph=SKIP_SPACES_GRAPH)
#     errors = []
#     if exp_match != match:
#         errors.append(f'exp match {exp_match} != {match}')
#     if exp_span != span:
#         errors.append(f'exp span {exp_span} != {span}')
#     assert not errors, '\t' + '; '.join(errors)

# TODO: def test_levenshtein_table__max_distance
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
        ("cat", "the cat sat", 1.0, ["cat"]),
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
def test_levenshtein_substrings_search_cases(query, string, min_similarity, expected: list[str]):
    result = levenshtein.levenshtein_substrings_search(query, string, min_similarity, mode=LevenshteinDistanceMode.SUBSTRING, proximity_graph=SKIP_SPACES_GRAPH)
    result = [string[slice(*span)] for span in result]
    assert result == expected
