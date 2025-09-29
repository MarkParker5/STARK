import logging

logger = logging.getLogger(__name__)
from typing import Generator

import numpy as np

'''
Directional proximity between characters, used for calculating the cost of substitution, insertion, and deletion.
'''
PROX_MED = 0.5
PROX_LOW = 0.25
type ProximityGraph = dict[str, dict[str, float]]
SIMPLEPHONE_PROXIMITY_GRAPH: ProximityGraph = {
    'w': {'f': PROX_MED, 'a': PROX_LOW, 'y': PROX_LOW},
    'y': {'a': PROX_LOW, 'w': PROX_LOW},
    'a': {'y': PROX_LOW, 'w': PROX_LOW, '-': PROX_LOW}, # '-' for deletion
    'f': {'w': PROX_MED},
    ' ': {'-': 0},
    '-': {'a': PROX_LOW, ' ': 0}, # insertion
}

def levenshtein_distance(
    s1: str,
    s2: str,
    max_distance: float | None = None,
    skip_spaces: bool = False,
    square: bool = False,
    proximity_graph: ProximityGraph = {}
) -> tuple[float, int]:
    '''
    Optimized Levenshtein distance calculation with early return when distance exceeds threshold, with proximity graph for chars, and skipping spaces.

    s2 should be the longer string.

    Square: limits the maximum distance to the length of the longer string.

    Returns the distance and the length of the match.

    The length is only used to adjust the length of the matched s2 substring with spaces (basically len of s2 + spaces in s2)
    '''

    logger.debug(f"Arguments: s1='{s1}', s2='{s2}', max_distance={max_distance}, skip_spaces={skip_spaces}, square={square}, proximity_graph={proximity_graph}")

    abs_max_distance = min(len(s1), len(s2)) if square else max(len(s1), len(s2))
    max_distance = max_distance if max_distance is not None else abs_max_distance

    # Shortcut full match

    if s1 == s2:
        return (0, len(s2))

    if skip_spaces and s1.replace(' ', '') == s2.replace(' ', ''):
        return (0, len(s2))

    # Handle empty string cases

    if not s1 or (skip_spaces and s1.replace(' ', '') == ''):
        return (len(s2), 0)
    if not s2 or (skip_spaces and s2.replace(' ', '') == ''):
        return (len(s2), 0)

    # Start the main part

    n = len(s1)
    m = len(s2)

    dp = np.full((n + 1, m + 1), 1e6, dtype=float)
    dp[:, 0] = np.arange(n + 1)
    dp[0, :] = np.arange(m + 1)
    furthest_k = 0

    # start substring distance evalution (filling DP matrix rows)
    for j in range(1, n + 1):

        k = 0 # TODO: try going diagonal-ish to skip bottom-left corner
        dk = 0
        dn = n if square else m

        # column loop (filling row cells)
        while k < dn: # limit the distance to square of the first string length + spaces compensation
            dk += 1
            k += 1

            if k - 1 >= m:
                break # string end reached

            if s1[j - 1] == s2[dk - 1]: # full match, no cost added
                dp[j, k] = dp[j - 1, k - 1]

            elif s2[dk - 1] == ' ' and skip_spaces: # skip space, no cost added
                dp[j, k] = dp[j - 1, k - 1]
                dn += 1 # check one more char to compensate the space
                k -= 1

            else: # different characters, calculate additional cost
                sub_cost = proximity_graph.get(s1[j - 1], {}).get(s2[k - 1], 1.0)
                ins_cost = proximity_graph.get(s1[j - 1], {}).get('-', 1.0)
                del_cost = proximity_graph.get('-', {}).get(s2[k - 1], 1.0)
                # logger.debug(f'Char mismatch: {j=}"{s1[j - 1]}" -> {k=}"{s2[k - 1]}"; {sub_cost=} {ins_cost=} {del_cost=}')

                dp[j, k] = min( # save min full cost for this step
                    dp[j - 1, k] + del_cost,    # deletion
                    dp[j, k - 1] + ins_cost,    # insertion
                    dp[j - 1, k - 1] + sub_cost # substitution
                )

            # cell-level early break: if this path already too far (derivative sign turned positive) - skip this row and try next
            if dp[j, k] > dp[j, k-1]:
                break

            furthest_k = max(furthest_k, dk)

        # row-level early break: full stop if the best in this row is too far, it can't be better than this
        # if (distance := np.min(dp[j, :])) > max_distance:
        #     logger.debug(f"\nLevenshtein table for '{s1}' vs '{s2}' early return:\n{dp.astype(int)}")
        #     return float(distance), int(furthest_k) # don't really care about the length here since the match is canceled early

    # Debug: log DP table before return
    logger.debug(f"\nLevenshtein table for '{s1}' vs '{s2}', max_distance={max_distance}\n%s", dp.astype(int))
    distance = np.min(dp[-1, :])
    # distance = np.min(dp[-1, :furthest_k])
    # distance = dp[-1, furthest_k]
    length = np.argmin(dp[-1, :])
    # length = furthest_k
    logger.debug(f"Returning distance: {distance}; {np.argmin(dp[-1, :])=} {furthest_k=}")
    return float(distance), int(length)

def levenshtein_similarity(
    s1: str,
    s2: str,
    min_similarity: float = 0,
    skip_spaces: bool = False,
    square: bool = False,
    proximity_graph: ProximityGraph = {}
) -> tuple[float, int]:
    '''
    Computes the similarity between two strings using the Levenshtein distance. Output: 0...1 where 1 indicates perfect similarity and 0 indicates perfect mismatch. The length of s1 is used to calculate the maximum possible distance. Returns the similarity score and the number of spaces skipped.
    '''

    if not s1 or not s2:
        return 0, len(s1) # avoid zero division

    tolerance = 1 - min_similarity
    max_total_distance = len(s1.replace(' ', '') if skip_spaces else s1)
    max_allowed_distance = round(max_total_distance * tolerance)
    distance, length = levenshtein_distance(s1, s2, max_allowed_distance, skip_spaces, square=square, proximity_graph=proximity_graph)

    return 1 - distance / max_total_distance, length

def levenshtein_match(
    s1: str,
    s2: str,
    min_similarity: float,
    skip_spaces: bool = False,
    square: bool = False,
    proximity_graph: ProximityGraph = {}
) -> tuple[bool, int]:
    similarity, length = levenshtein_similarity(s1, s2, min_similarity, skip_spaces, square=square, proximity_graph=proximity_graph)
    return similarity >= min_similarity, length

def levenshtein_substrings_search(
    query: str,
    string: str,
    min_similarity: float,
    skip_spaces: bool = False,
    proximity_graph: ProximityGraph = {}
) -> Generator[str, None, None]:
    '''
    Searches substrings similar to `query` in `string`. Weighted by similarity, optimized with early exists, spaces are skipped. min_similarity=0.9 means not less than 90% of strings matches.
    '''

    if not query or not string:
        return

    query = query.replace(' ', '')
    string = string.strip()
    n = len(query)
    m = len(string)

    # iterate over each candidate substring of `string` (sliding window)
    i = -1
    while i < m - n + 1:
        i += 1
        if string[i] == ' ':
            # string with leading space and without are the same, so we can skip it
            continue

        is_match, length = levenshtein_match(query, string[i:], min_similarity, skip_spaces=skip_spaces, square=True, proximity_graph=proximity_graph)
        if is_match:
            yield string[i:i + length].strip() # TODO: return span indices
            i += length # skip matched substring; TODO: review cases of overlapping improving or degrading results

# TODO: CHECK: cutting the left part of the string can give better results
# TODO: CHECK: right part isn't cutting well too
