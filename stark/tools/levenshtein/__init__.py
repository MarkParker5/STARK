from typing import TypedDict, Unpack

import numpy

from stark.tools.common.span import Span
from .levenshtein import (
    LevenshteinParams,
    levenshtein_matrix as _levenshtein_matrix,
    levenshtein_distance as _levenshtein_distance,
    levenshtein_similarity as _levenshtein_similarity,
    levenshtein_match as _levenshtein_match,
    levenshtein_distance_substring as _levenshtein_distance_substring,
    levenshtein_similarity_substring as _levenshtein_similarity_substring,
    levenshtein_search_substring as _levenshtein_search_substring,
)

# Models

type ProximityGraph = dict[str, dict[str, float]]


class LevenshteinParamsDict(TypedDict, total=False):
    s1: str
    s2: str
    proximity_graph: ProximityGraph
    max_distance: float
    ignore_prefix: bool
    ignore_suffix: bool
    narrow: bool
    early_return: bool
    lower: bool


# Constants

PROX_MED = 0.5
PROX_LOW = 0.25
PROX_MIN = 0.01
SIMPLEPHONE_PROXIMITY_GRAPH: ProximityGraph = {
    "w": {"f": PROX_MED, "a": PROX_LOW, "y": PROX_LOW},
    "y": {"a": PROX_LOW, "w": PROX_LOW},
    "a": {"y": PROX_LOW, "w": PROX_LOW, "-": PROX_LOW},  # '-' for deletion
    "f": {"w": PROX_MED},
    " ": {"-": PROX_MIN},  # ignore spaces
    "-": {"a": PROX_LOW, " ": PROX_MIN},  # insertion
}
SKIP_SPACES_GRAPH = {" ": {"-": PROX_MIN}, "-": {" ": PROX_MIN}}

# Functions


def levenshtein_matrix(
    **kwargs: Unpack[LevenshteinParamsDict],
) -> numpy.ndarray:
    return _levenshtein_matrix(LevenshteinParams(**kwargs))


# Wrappers


def levenshtein_distance(**kwargs: Unpack[LevenshteinParamsDict]) -> float:
    return _levenshtein_distance(LevenshteinParams(**kwargs))


def levenshtein_similarity(
    threshold: float = 0, **kwargs: Unpack[LevenshteinParamsDict]
) -> float:
    return _levenshtein_similarity(threshold, LevenshteinParams(**kwargs))


def levenshtein_match(
    threshold: float = 0, **kwargs: Unpack[LevenshteinParamsDict]
) -> bool:
    return _levenshtein_match(threshold, LevenshteinParams(**kwargs))


# Substring


def levenshtein_distance_substring(
    **kwargs: Unpack[LevenshteinParamsDict],
) -> list[tuple[Span, float]]:
    return _levenshtein_distance_substring(LevenshteinParams(**kwargs))


def levenshtein_similarity_substring(
    threshold: float = 0, **kwargs: Unpack[LevenshteinParamsDict]
) -> list[tuple[Span, float]]:
    return _levenshtein_similarity_substring(threshold, LevenshteinParams(**kwargs))


def levenshtein_search_substring(
    threshold: float = 0, **kwargs: Unpack[LevenshteinParamsDict]
) -> list[tuple[Span, float]]:
    return _levenshtein_search_substring(threshold, LevenshteinParams(**kwargs))
