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

# # Shortcut full match

# if s1 == s2:
#     return (0, len(s2))

# if skip_spaces and s1.replace(' ', '') == s2.replace(' ', ''):
#     return (0, len(s2))

# # Handle empty string cases

# if not s1 or (skip_spaces and s1.replace(' ', '') == ''):
#     return (len(s2), 0)
# if not s2 or (skip_spaces and s2.replace(' ', '') == ''):
#     return (len(s2), 0)

def levenshtein_table(
    s1: str,
    s2: str,
    max_distance: float | None = None,
    square: bool = False,
    narrow: bool = True,
    proximity_graph: ProximityGraph = {},
) -> np.ndarray:
    '''
    Calculates the Levenshtein distance between two strings s1 and s2.

    '''

    abs_max_distance = min(len(s1), len(s2)) if square else max(len(s1), len(s2))
    max_distance = max_distance if max_distance is not None else abs_max_distance

    # Start the main part

    s1_len = len(s1)
    s2_len = len(s2)

    matrix = np.full((s1_len + 1, s2_len + 1), 1e6, dtype=float)
    matrix[:, 0] = np.arange(s1_len + 1)
    matrix[0, :] = np.arange(s2_len + 1)
    best_column = 0

    # start substring distance evalution (filling matrix rows)
    for row_i in range(1, s1_len + 1):

        char1 = s1[row_i - 1]

        # column loop (filling row cells)
        start_column = max(1, best_column-1)
        for cell_i in range(start_column, s2_len + 1):

            char2 = s2[cell_i - 1]

            if char1 == char2: # full match, no cost added
                cell_value = matrix[row_i - 1, cell_i - 1]

            else: # different characters, calculate additional cost

                # get costs for char edits from the proximity graph
                del_cost = proximity_graph.get(char1, {}).get('-', 1.0)
                ins_cost = proximity_graph.get('-', {}).get(char2, 1.0)
                sub_cost = proximity_graph.get(char1, {}).get(char2, 1.0)

                cell_value = min( # save min full cost for this step
                    matrix[row_i - 1, cell_i] + del_cost,    # deletion
                    matrix[row_i, cell_i - 1] + ins_cost,    # insertion
                    matrix[row_i - 1, cell_i - 1] + sub_cost # substitution
                )

            matrix[row_i, cell_i] = cell_value

            # early stop by max distance limit
            if (
                cell_value > matrix[row_i, cell_i-1] # derivative sign turned positive -> the prev was the best
                and matrix[row_i, cell_i-1] > max_distance # the best is worse than limit
            ):
                return matrix

            # cut off corners if optimisation param is set
            if narrow:
                # remove bottom left corner
                if cell_value < matrix[row_i, cell_i-1]:
                    # fill next row from the column to the left of the current column by skipping leftmost cells
                    best_column = cell_i

                # remove top right corner
                if (
                    cell_value > matrix[row_i, cell_i-1] # derivative sign turned positive -> the prev was the best
                    and row_i != s1_len # don't skip the last row to set the right bottom (-1;-1) cell which represents the full distance
                ):
                    # end this row if the path is already too far
                    break

    # return fully filled dp
    return matrix

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

    dp = levenshtein_table(s1, s2, max_distance, skip_spaces, square, proximity_graph)
    distance = np.min(dp[-1, :])
    # distance = np.min(dp[-1, :furthest_k])
    # distance = dp[-1, furthest_k]
    # length = furthest_k
    length = np.argmin(dp[-1, :])
    logger.debug(f"Returning {distance=} {length=}")
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

if __name__ == '__main__':

    dp = levenshtein_table(
        # s1 := 'abcl n k n p k',
        # s2 := 'abclnknpk sit amet',
        # s1 := 'Facebooke',
        # s2 := 'google',
        s1 := 'google',
        s2 := 'Facebookeeee',
        narrow=True,
        proximity_graph={
            ' ': {'-': 0}, # space removed from s1
            '-': {' ': 0} # space inserted in s1
        }
    )

    # Plot:

    import matplotlib.pyplot as plt
    import numpy as np

    def auto_figsize(arr: np.ndarray, cell_w: float = 0.6, cell_h: float = 0.6) -> tuple[float, float]:
        return arr.shape[1] * cell_w, arr.shape[0] * cell_h

    fig, ax = plt.subplots(figsize=auto_figsize(dp))
    masked = np.ma.masked_where(dp >= 1e6, dp)
    cax = ax.matshow(masked, cmap='viridis', alpha=0.7)
    for (i, j), val in np.ndenumerate(dp):
        if val < 1e6:
            weight = 'bold' if val == 0 else 'normal'
            ax.text(j, i, f'{val:.1f}', va='center', ha='center', color='white', fontsize=8, fontweight=weight)
    ax.set_xticks(range(len(s2)+1))
    ax.set_yticks(range(len(s1)+1))
    ax.set_xticklabels(['s2']+list(s2))
    ax.set_yticklabels(['s1']+list(s1))
    plt.colorbar(cax)
    plt.tight_layout()
    plt.show()
