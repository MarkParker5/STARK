import numpy as np
from stark.tools.common.span import Span

PROX_MED: float
PROX_LOW: float
PROX_MIN: float
SIMPLEPHONE_PROXIMITY_GRAPH: dict[str, dict[str, float]]
SKIP_SPACES_GRAPH: dict[str, dict[str, float]]

class LevenshteinParams:
    s1: str
    s2: str
    max_distance: float
    proximity_graph: dict[str, dict[str, float]]
    ignore_prefix: bool
    ignore_suffix: bool
    narrow: bool
    early_return: bool
    lower: bool

    def __init__(
        self,
        s1: str,
        s2: str,
        proximity_graph: dict[str, dict[str, float]],
        max_distance: float = ...,
        ignore_prefix: bool = ...,
        ignore_suffix: bool = ...,
        narrow: bool = ...,
        early_return: bool = ...,
        lower: bool = ...,
    ): ...
    def proximity(self, c1: str, c2: str) -> float: ...

def levenshtein_matrix(p: LevenshteinParams) -> np.ndarray: ...
def levenshtein_distance(p: LevenshteinParams) -> float: ...
def levenshtein_similarity(threshold: float, p: LevenshteinParams) -> float: ...
def levenshtein_match(threshold: float, p: LevenshteinParams) -> bool: ...
def levenshtein_distance_substring(
    p: LevenshteinParams,
) -> list[tuple[Span, float]]: ...
def levenshtein_similarity_substring(
    threshold: float, p: LevenshteinParams
) -> list[tuple[Span, float]]: ...
def levenshtein_search_substring(
    threshold: float, p: LevenshteinParams
) -> list[tuple[Span, float]]: ...
