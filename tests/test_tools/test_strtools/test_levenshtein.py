import pytest

from stark.tools.levenshtein import (
    SIMPLEPHONE_PROXIMITY_GRAPH,
    SKIP_SPACES_GRAPH,
    LevenshteinParams,
    levenshtein_distance,
    levenshtein_match,
    levenshtein_search_substring,
    levenshtein_similarity,
)

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

# --- Proximity Graphs ---

@pytest.mark.parametrize(
    "a,b,exp_max_distance",
    [
        # chars
        ("ab", "ba", 1.25),
        ("w", "f", 0.5),
        ("wt", "ft", 0.5),
        ("wt", "at", 0.5),
        # words
        ('ASPTAFA', 'SPTFA', 0.75),
        ('AWATAAA', 'AFATAAA', 0.5),
        ('TSNWTSN', 'TSNFTSN', 0.5),
        ('AMWTSN', 'AMAATSN', 0.5),
        ('AMATSNTRKNS', 'AMTSNTRKNS', 0.5),
    ]
)
def test_levenshtein_distance_proximity(a: str, b: str, exp_max_distance: float) -> None:
    print(f'{a=} {b=}')
    params = LevenshteinParams(s1=a, s2=b, proximity_graph=SIMPLEPHONE_PROXIMITY_GRAPH)
    distance = levenshtein_distance(params)
    assert distance <= exp_max_distance, f'exp distance {exp_max_distance:.2f} < {distance:.2f}'

@pytest.mark.parametrize(
    "a,b,exp_distance",
    [
        ("lnk npk", "lnknpk", 0),
        ("lnknpk", "lnk npk", 0),
        ("lnknpk", "ln kn pk", 0),
        ("ln kn pk", "lnknpk", 0),
        ("lnknpk", "l n k n p k", 0),
        ("l n k n p k", "lnknpk", 0),
    ]
)
def test_levenshtein_distance_skip_spaces(a: str, b: str, exp_distance: float) -> None:
    print(f'{a=} {b=}')
    params = LevenshteinParams(s1=a, s2=b, proximity_graph=SKIP_SPACES_GRAPH)
    distance = levenshtein_distance(params)
    assert distance == pytest.approx(exp_distance, abs=0.1), f'exp distance {exp_distance:.2f} != {distance:.2f}'

# --- Substring Distance/Similarity/Search ---

@pytest.mark.parametrize(
    "a,b,min_similarity,exp_spans",
    [
        # basic edge cases for debug
        # checking similarity limit doesn't return too early
        ("abc", "xxx abc xxx", 0, [(4, 7)]),
        ("abc", "xxx abc xxx", 0.5, [(4, 7)]),
        ("abc", "xxx abc xxx", 0.9, [(4, 7)]),
        ("abc", "xxx abc xxx", 1, [(4, 7)]),
        # searching substring inside string
        ("cat", "the bat sat", 1.0, []),
        ("cat", "the cat sat", 1.0, [(4, 7)]),
        ("cat", "the bcat dog", 0.50, [(5, 8)]),
        ("cat", "the bat sat", 0.6, [(4, 7), (8, 11)]),
        ("cat", "abc cat def cat ghj cat klm", 1.0, [(4, 7), (12, 15), (20, 23)]),
        # two matches
        ("cat", "the bat and sat", 0.6, [(4, 7), (12, 15)]),
        # with spaces
        ("lnknpk", "lorem ispum lnknpk sit amet", 0.9, [(12, 18)]),
        ("lnknpk", "lorem ispum ln kn pk sit amet", 0.9, [(12, 20)]),
        ("ln kn pk", "lorem ispum lnknpk sit amet", 0.9, [(12, 18)]),
        ("ln kn pk", "lorem ispum ln kn pk sit amet", 0.9, [(12, 20)]),
        ("lnknpk", "lorem ispum ln kn pk sit amet lnk npk foo bar baz", 0.9, [(12, 20), (30, 37)]),
    ]
)
def test_levenshtein_search_substring(a: str, b: str, min_similarity: float, exp_spans: list[tuple[int, int]]) -> None:
    print(f'{a=} {b=}')
    longer = a if len(a) > len(b) else b
    shorter = a if len(a) <= len(b) else b
    params = LevenshteinParams(s1=a, s2=b, proximity_graph=SKIP_SPACES_GRAPH, ignore_prefix=True, early_return=False)
    matches = levenshtein_search_substring(params, min_similarity)
    result = [(span.start, span.end) for span, _ in matches]
    errors = []
    if not exp_spans:
        assert not result, f'Unexpected matches found: {matches}'
        return
    assert result, 'No matches found'
    assert len(result) == len(exp_spans), f'Expected {len(exp_spans)} matches, got {len(result)}: {matches}'
    for i in range(len(result)):
        if result[i] != exp_spans[i]:
            errors.append(f'exp spans {exp_spans} != {result} - matched "{longer[matches[0][0].slice]}"')
        p = LevenshteinParams(shorter, longer[matches[0][0].slice], proximity_graph=SKIP_SPACES_GRAPH)
        if levenshtein_distance(p) / len(shorter) > (1 - min_similarity):
            errors.append(f'Unexpected substr: exp {shorter} != {longer[matches[0][0].slice]}')
    assert not errors, '\t' + '; '.join(errors)
