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

def levenshtein_matrix(
    s1: str,
    s2: str,
    max_distance: float | None = None,
    narrow: bool = True,
    proximity_graph: ProximityGraph = {},
) -> np.ndarray:
    '''
    Calculates the Levenshtein distance between two strings s1 and s2.
    Max distance stops the calculations early if the distance exceeds the max_distance for better performance.
    Narrow mode minimizes the number of operations, limits max distance to the smaller of the two strings; calculates "substring" match instead of full string match.
    Proximity graph allows tweaking the cost of operations for any character (default cost is 1), for example, based on phonetic similarity, keyboard proximity, char aliases, costless whitespaces, etc.
    '''

    abs_max_distance = min(len(s1), len(s2)) if narrow else max(len(s1), len(s2))
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

            if char1 == char2 and matrix[row_i - 1, cell_i - 1] != 1e6: # check for 1e6 in narrow mode
                # full match, no cost added
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

            matrix[row_i, cell_i] = cell_value = min(cell_value, 1e6)
            logger.debug(f"Cell ({row_i}={char1}, {cell_i}={char2}) value: {cell_value}")

            # cut off corners if optimisation param is set
            if narrow:
                # remove bottom left corner
                if cell_value < matrix[row_i, cell_i-1]:
                    # fill next row from the column to the left of the current column by skipping leftmost cells
                    best_column = cell_i

                # remove top right corner
                if (
                    cell_value > matrix[row_i, cell_i-1] # derivative sign is positive -> the prev was the best
                    and row_i != s1_len # don't skip the last row to set the right bottom (-1;-1) cell which represents the full distance
                ):
                    # end this row if the path is already too far
                    logger.debug('Skipping row')
                    break

        # early stop by max distance limit
        if matrix[row_i, best_column] > max_distance: # the best is worse than limit
            logger.debug('Distance limit')
            return matrix

    # return fully filled dp
    return matrix

def levenshtein_distance(
    s1: str,
    s2: str,
    max_distance: float | None = None,
    narrow: bool = False,
    proximity_graph: ProximityGraph = {}
) -> tuple[int, float]:
    '''
    Returns the best length of s2 substr for levenshtein match with s1, and the best distance for that length
    '''
    matrix = levenshtein_matrix(s1, s2, max_distance, narrow, proximity_graph)
    best_length = np.argmin(matrix[-1, :])
    best_distance_for_length = matrix[-1, best_length]
    logger.debug(f"Returning {best_length=} {best_distance_for_length=}")
    return int(best_length), float(best_distance_for_length)

def levenshtein_similarity(
    s1: str,
    s2: str,
    min_similarity: float = 0,
    narrow: bool = False,
    proximity_graph: ProximityGraph = {}
) -> tuple[int, float]:
    '''
    Computes the similarity between two strings using the Levenshtein distance. Output: 0...1 where 1 indicates perfect similarity and 0 indicates perfect mismatch. The length of s1 is used to calculate the maximum possible distance. Returns the best length of s2 to maximally match s1, and the similarity score.
    '''

    if not s1 or not s2:
        return 0, len(s1) # avoid zero division

    tolerance = 1 - min_similarity
    # max_total_distance = len(s1.replace(' ', '') if skip_spaces else s1)
    max_total_distance = min(len(s1), len(s2)) if narrow else max(len(s1), len(s2))
    max_allowed_distance = round(max_total_distance * tolerance)
    length, distance = levenshtein_distance(s1, s2, max_allowed_distance, narrow, proximity_graph=proximity_graph)

    return length, 1 - distance / max_total_distance

def levenshtein_match(
    s1: str,
    s2: str,
    min_similarity: float,
    narrow: bool = False,
    proximity_graph: ProximityGraph = {}
) -> tuple[int, bool]:
    '''
    Checks if two strings are similar enough based on the Levenshtein distance. Returns the best length of s2 to maximally match s1, and whether it's a match. Length value is only meaningful when the match is true.
    '''
    length, similarity = levenshtein_similarity(s1, s2, min_similarity, narrow, proximity_graph=proximity_graph)
    return length, similarity >= min_similarity

def levenshtein_substrings_search(
    query: str,
    string: str,
    min_similarity: float,
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

        is_match, length = levenshtein_match(query, string[i:], min_similarity, narrow=True, proximity_graph=proximity_graph)
        if is_match:
            yield string[i:i + length].strip() # TODO: return span indices
            i += length # skip matched substring;
            # TODO: review cases of overlapping improving or degrading results
            # TODO: cutting the left part of the string can give better results
            # TODO: right part isn't cutting well too

if __name__ == '__main__':

    logging.basicConfig()
    logger.setLevel(logging.DEBUG)

    dp = levenshtein_matrix(
        # s1 := 'abcl n k n p k',
        # s2 := 'abclnknpk sit amet',
        # s1 := 'abcl n p n k zzz',
        # s2 := 'abclnknpk sit amet',
        # s1 := 'Facebookeeee',
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
