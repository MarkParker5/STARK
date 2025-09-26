from typing import Generator

import numpy as np

'''
Directional proximity between characters, used for calculating the cost of substitution, insertion, and deletion.
'''
PROX_MED = 0.5
PROX_LOW = 0.25
PROXIMITY_GRAPH: dict[str, dict[str, float]] = {
    'w': {'f': PROX_MED, 'a': PROX_LOW, 'y': PROX_LOW},
    'y': {'a': PROX_LOW, 'w': PROX_LOW},
    'a': {'y': PROX_LOW, 'w': PROX_LOW, '-': PROX_LOW}, # '-' for deletion
    'f': {'w': PROX_MED},
    ' ': {'-': 0},
    '-': {'a': PROX_LOW, ' ': 0}, # insertion
}

def levenshtein_distance(s1: str, s2: str, max_distance: float | None = None, skip_spaces: bool = False) -> tuple[float, int]:
    '''
    Optimized Levenshtein distance calculation with early return when distance exceeds threshold, with proximity graph for chars, and skipping spaces.
    Returns the distance and the length of the match.
    '''

    if s1 == s2:
        return 0, 0

    if skip_spaces and s1.replace(' ', '') == s2.replace(' ', ''):
        return 0, 0

    n = len(s1)
    m = len(s2)

    dp = np.full((n + 1, m + 1), 1e6, dtype=float)
    dp[:, 0] = np.arange(n + 1)
    dp[0, :] = np.arange(m + 1)
    furthest_k = 0

    # start substring distance evalution (filling DP matrix rows)
    for j in range(1, n + 1):

        k = 0
        dn = n

        # column loop (filling row cells)
        while k < dn: # limit the distance to square of the first string length + spaces compensation
            k += 1

            if k - 1 >= m:
                break # string end reached

            if s1[j - 1] == s2[k - 1]: # full match, no cost added
                dp[j, k] = dp[j - 1, k - 1]

            elif s2[k - 1] == ' ' and skip_spaces: # skip space, no cost added
                dp[j, k] = dp[j - 1, k - 1]
                dn += 1

            else: # different characters, calculate additional cost
                sub_cost = PROXIMITY_GRAPH.get(s1[j - 1], {}).get(s2[k - 1], 1.0)
                ins_cost = PROXIMITY_GRAPH.get(s1[j - 1], {}).get('-', 1.0)
                del_cost = PROXIMITY_GRAPH.get('-', {}).get(s2[k - 1], 1.0)

                dp[j, k] = min( # save min full cost for this step
                    dp[j - 1, k] + del_cost,    # deletion
                    dp[j, k - 1] + ins_cost,    # insertion
                    dp[j - 1, k - 1] + sub_cost # substitution
                )

            furthest_k = max(furthest_k, k)

            # cell-level early break: if this path already too far - skip and try next
            if dp[j, k] > max_distance:
                break
        # row-level early break: full stop if the best in this row is too far, it can't be better than this
        if (distance := np.min(dp[j, :])) > max_distance:
            return distance, furthest_k

    # distance = np.min(dp[-1, :furthest_k+1])
    distance = dp[-1, furthest_k]
    return distance, furthest_k + 1

def levenshtein_similarity(s1: str, s2: str, min_similarity: float = 0, skip_spaces: bool = False) -> tuple[float, int]:
    '''
    Computes the similarity between two strings using the Levenshtein distance. Output: 0...1 where 1 indicates perfect similarity and 0 indicates perfect mismatch. The length of s1 is used to calculate the maximum possible distance. Returns the similarity score and the number of spaces skipped.
    '''

    if not s1 or not s2:
        return 0, 0 # avoid zero division

    tolerance = 1 - min_similarity
    max_total_distance = len(s1.replace(' ', '') if skip_spaces else s1)
    max_allowed_distance = round(max_total_distance * tolerance)
    distance, length = levenshtein_distance(s1, s2, max_allowed_distance, skip_spaces)

    return 1 - distance / max_total_distance, length

def levenshtein_substrings_search(query: str, string: str, min_similarity: float) -> Generator[str, None, None]:
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
        similarity, length = levenshtein_similarity(query, string[i:], min_similarity, skip_spaces=True)
        if similarity >= min_similarity:
            yield string[i:i + length].strip() # TODO: return span indices
            i += length
            # TODO: CHECK: cutting the left part of the string can give better results
            # TODO: CHECK: right part isn't cutting well too
