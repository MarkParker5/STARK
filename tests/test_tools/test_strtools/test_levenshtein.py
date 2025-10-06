import pytest

from stark.tools.levenshtein import (
    SIMPLEPHONE_PROXIMITY_GRAPH,
    LevenshteinParams,
    levenshtein_distance,
    levenshtein_distance_substring,
    levenshtein_match,
    levenshtein_search_substring,
    levenshtein_similarity,
)

SKIP_SPACES_GRAPH = {
    ' ': {'-': 0.0},
    '-': {' ': 0.0}
}

# TODO: test early stop

# --- Full String Distance/Similarity/Match ---

@pytest.mark.parametrize(
    "a,b,exp_distance",
    [
        ("abc", "yabcx", 2),
        ("yabcx", "abc", 2),
        ("flaw", "lawn", 2),
        ("lawn", "flaw", 2),
        ("sitting", "kitten", 3),
        ("kitten", "sitting", 3),
        ("saturday", "sunday", 3),
        ("sunday", "saturday", 3),
        ("elephant", "relevant", 3),
        ("relevant", "elephant", 3),
        ("abc", "abcyz", 2),
        ("abcyz", "abc", 2),
        ("abc", "xxabcyz", 4),
        ("xxabcyz", "abc", 4),
        ("flaw", "lawn", 2),
        ("lawn", "flaw", 2),
        ("elephant", "relevant", 3),
        ("relevant", "elephant", 3),
        ("sitting", "kitten", 3),
        ("kitten", "sitting", 3),
        ("saturday", "sunday", 3),
        ("sunday", "saturday", 3),
        ("lnknpk", "ln kn pk", 2),
        ("ln kn pk", "lnknpk", 2),
        ("lnk npk", "lnknpk", 1),
    ]
)
def test_levenshtein_distance_full(a: str, b: str, exp_distance: float) -> None:
    print(f'{a=} {b=}')
    params = LevenshteinParams(s1=a, s2=b)
    distance = levenshtein_distance(params)
    errors = []
    if distance != exp_distance:
        errors.append(f'exp distance {exp_distance:.2f} != {distance:.2f}')
    assert not errors, '\t' + '; '.join(errors)

@pytest.mark.parametrize(
    "a,b,min_similarity,exp_similarity",
    [
        ("abc", "abc", 0.0, 1.0),
        ("abc", "abx", 0.0, 2/3),
        ("abc", "xyz", 0.0, 0.0),
        ("kitten", "sitting", 0.0, 4/7),
        ("saturday", "sunday", 0.0, 5/8),
    ]
)
def test_levenshtein_similarity_full(a: str, b: str, min_similarity: float, exp_similarity: float) -> None:
    print(f'{a=} {b=}')
    params = LevenshteinParams(s1=a, s2=b)
    similarity = levenshtein_similarity(params, min_similarity)
    errors = []
    if not similarity == pytest.approx(exp_similarity, abs=1e-6):
        errors.append(f'exp similarity {exp_similarity:.2f} != {similarity:.2f}')
    assert not errors, '\t' + '; '.join(errors)

@pytest.mark.parametrize(
    "a,b,min_similarity,exp_match",
    [
        ("abc", "abc", 1.0, True),
        ("abc", "abx", 1.0, False),
        ("abc", "abx", 0.5, True),
        ("kitten", "sitting", 0.5, True),
        ("kitten", "sitting", 0.7, False),
    ]
)
def test_levenshtein_match_full(a: str, b: str, min_similarity: float, exp_match: bool) -> None:
    print(f'{a=} {b=}')
    params = LevenshteinParams(s1=a, s2=b)
    match = levenshtein_match(params, min_similarity)
    errors = []
    if match != exp_match:
        errors.append(f'exp match {exp_match} != {match}')
    assert not errors, '\t' + '; '.join(errors)

# --- Substring Distance/Similarity/Search ---

@pytest.mark.parametrize(
    "a,b,exp_span,exp_distance",
    [
        ("abc", "abcyz", (0, 3), 0),
        ("abcyz", "abc", (0, 3), 0),
        ("abc", "xxxabcxxx", (3, 6), 0),
        ("xxxabczzz", "abc", (3, 6), 0),
        ("flaw", "lawn", (0, 3), 1),
        ("lawn", "flaw", (1, 4), 1),
        ("elephant", "relevant", (1, 8), 2),
        ("relevant", "elephant", (0, 8), 3),
        ("sitting", "kitten", (1, 6), 2),
        ("kitten", "sitting", (1, 6), 2),
        ("saturday", "sunday", (2, 8), 2),
        ("sunday", "saturday", (2, 8), 2),
        ("lnknpk", "ln kn pk", (0, 8), 0),
        ("ln kn pk", "lnknpk", (0, 8), 0), # TODO: test skip_spaces separately
        ("lnk npk", "lnknpk", (0, 7), 0),
    ]
)
def test_levenshtein_distance_substring(a: str, b: str, exp_span: tuple[int, int], exp_distance: float) -> None:
    print(f'{a=} {b=}')
    params = LevenshteinParams(s1=a, s2=b, proximity_graph=SKIP_SPACES_GRAPH, ignore_prefix=True, max_distance=3)
    matches = list(levenshtein_distance_substring(params)) # TODO: use just match with ignore flags here, use substring with multiple matches separately
    errors = []
    if not matches:
        errors.append(f"No matches, expected {exp_span=} {exp_distance=}")
    else:
        # assert len(matches) == 1, f"Expected one match {exp_span=} {exp_distance=}, got {matches=}"
        span, distance = matches[0]
        if (span.start, span.end) != exp_span:
            errors.append(f'exp span {exp_span} != {(span.start, span.end)}')
        if distance != exp_distance:
            errors.append(f'exp distance {exp_distance:.2f} != {distance:.2f}')
    assert not errors, '\t' + '; '.join(errors)

@pytest.mark.parametrize(
    "a,b,min_similarity,exp_spans",
    [
        ("cat", "the cat sat", 1.0, [(4, 7)]),
        ("cat", "the bat sat", 0.60, [(4, 7), (8, 11)]),
        ("cat", "the bcat dog", 0.50, [(5, 8)]),
        ("cat", "the bat sat", 1.0, []),
        ("lnknpk", "lorem ispum lnknpk sit amet", 1.0, [(13, 19)]),
        ("lnknpk", "lorem ispum ln kn pk sit amet", 1.0, [(13, 20)]),
        ("ln kn pk", "lorem ispum lnknpk sit amet", 1.0, [(13, 19)]),
        ("ln kn pk", "lorem ispum ln kn pk sit amet", 1.0, [(13, 20)]),
        ("lnknpk", "lorem ispum ln kn pk sit amet lnk npk foo bar baz", 1.0, [(13, 20), (27, 34)]),
        ("hello", "hello", 0.5, [(0, 5)]),
        ("hello", "world", 0.5, []),
        ("hello", "hellw", 1.0, []),
        ("hello", "world", 0.0, [(0, 5)]),
    ]
)
def test_levenshtein_search_substring(a: str, b: str, min_similarity: float, exp_spans: list[tuple[int, int]]) -> None:
    print(f'{a=} {b=}')
    params = LevenshteinParams(s1=a, s2=b)
    matches = levenshtein_search_substring(params, min_similarity)
    result = [(span.start, span.end) for span, _ in matches]
    errors = []
    if result != exp_spans:
        errors.append(f'exp spans {exp_spans} != {result}')
    assert not errors, '\t' + '; '.join(errors)

# --- Proximity Graphs ---

@pytest.mark.parametrize(
    "a,b,proximity_graph,exp_span,exp_distance",
    [
        ("ab", "ba", SIMPLEPHONE_PROXIMITY_GRAPH, (0, 2), 1.25),
        ("w", "f", SIMPLEPHONE_PROXIMITY_GRAPH, (0, 1), 0.5),
    ]
)
def test_levenshtein_distance_proximity(a: str, b: str, proximity_graph, exp_span: tuple[int, int], exp_distance: float) -> None:
    print(f'{a=} {b=}')
    params = LevenshteinParams(s1=a, s2=b, proximity_graph=proximity_graph)
    matches = list(levenshtein_distance_substring(params))
    errors = []
    if not matches:
        errors.append("No substring matches found")
    else:
        best_span, best_distance = min(matches, key=lambda x: x[1])
        if (best_span.start, best_span.end) != exp_span:
            errors.append(f'exp span {exp_span} != {(best_span.start, best_span.end)}')
        if best_distance != exp_distance:
            errors.append(f'exp distance {exp_distance:.2f} != {best_distance:.2f}')
    assert not errors, '\t' + '; '.join(errors)

# --- Skip Spaces/Whitespace Handling ---

@pytest.mark.parametrize(
    "a,b,exp_span,exp_distance",
    [
        ("lnknpk", "ln kn pk", (0, 8), 0),
        ("ln kn pk", "lnknpk", (0, 8), 0),
        ("lnk npk", "lnknpk", (0, 7), 0),
        ("lnknpk", "l n k n p k sit amet", (0, 11), 0),
        ("l n k n p k", "lnknpk sit amet", (0, 6), 0),
        ("cat sat", "cat", (0, 3), 0),
        ("the cat sat", "cat", (4, 7), 0),
        ("abc cat def cat ghj cat klm", "cat", (4, 7), 0),
    ]
)
def test_levenshtein_distance_skip_spaces(a: str, b: str, exp_span: tuple[int, int], exp_distance: float) -> None:
    print(f'{a=} {b=}')
    params = LevenshteinParams(s1=a, s2=b, proximity_graph=SKIP_SPACES_GRAPH)
    matches = list(levenshtein_distance_substring(params))
    errors = []
    if not matches:
        errors.append("No substring matches found")
    else:
        best_span, best_distance = min(matches, key=lambda x: x[1])
        if (best_span.start, best_span.end) != exp_span:
            errors.append(f'exp span {exp_span} != {(best_span.start, best_span.end)}')
        if best_distance != exp_distance:
            errors.append(f'exp distance {exp_distance:.2f} != {best_distance:.2f}')
    assert not errors, '\t' + '; '.join(errors)

@pytest.mark.parametrize(
    "a,b,min_similarity,exp_spans",
    [
        ("lnknpk", "lorem ispum lnknpk sit amet", 1.0, [(13, 19)]),
        ("lnknpk", "lorem ispum ln kn pk sit amet", 1.0, [(13, 20)]),
        ("ln kn pk", "lorem ispum lnknpk sit amet", 1.0, [(13, 19)]),
        ("ln kn pk", "lorem ispum ln kn pk sit amet", 1.0, [(13, 20)]),
        ("lnknpk", "lorem ispum ln kn pk sit amet lnk npk foo bar baz", 1.0, [(13, 20), (27, 34)]),
    ]
)
def test_levenshtein_search_skip_spaces(a: str, b: str, min_similarity: float, exp_spans: list[tuple[int, int]]) -> None:
    print(f'{a=} {b=}')
    params = LevenshteinParams(s1=a, s2=b, proximity_graph=SKIP_SPACES_GRAPH)
    matches = levenshtein_search_substring(params, min_similarity)
    result = [(span.start, span.end) for span, _ in matches]
    errors = []
    if result != exp_spans:
        errors.append(f'exp spans {exp_spans} != {result}')
    assert not errors, '\t' + '; '.join(errors)
