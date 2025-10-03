import logging
from enum import Enum, auto

from typing_extensions import NamedTuple

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

class Span(NamedTuple):
    start: int
    end: int

    @property
    def length(self) -> int:
        return self.end - self.start

    @classmethod
    @property
    def zero(cls) -> 'Span':
        return cls(0, 0)

    def __bool__(self) -> bool:
        return self.start != self.end

    def __repr__(self) -> str:
        return f'({self.start}, {self.end})'

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
    ignore_prefix: bool = False,
    ignore_suffix: bool = False,
) -> np.ndarray:
    '''
    Calculates the Levenshtein distance between two strings s1 and s2.
    Max distance stops the calculations early if the distance exceeds the max_distance for better performance.
    Narrow mode minimizes the number of operations, limits max distance to the smaller of the two strings; calculates "substring" match instead of full string match.
    Proximity graph allows tweaking the cost of operations for any character (default cost is 1), for example, based on phonetic similarity, keyboard proximity, char aliases, costless whitespaces, etc.
    s1 is rows, s2 is columns.
    If ignore_prefix is True, there is no penalty for prefix mismatches in s1 (like substring matching).
    If ignore_suffix is True, there is no penalty for suffix mismatches in s1 (like substring matching).
    '''
    narrow = False # TODO: review implementation, produces wrong results

    abs_max_distance = min(len(s1), len(s2)) if narrow else max(len(s1), len(s2))
    max_distance = max_distance if max_distance is not None else abs_max_distance

    # Start the main part

    s1_len = len(s1)
    s2_len = len(s2)

    matrix = np.full((s1_len + 1, s2_len + 1), 1e6, dtype=float)
    matrix[:, 0] = np.arange(s1_len + 1)
    matrix[0, :] = 0 if ignore_prefix else np.arange(s2_len + 1)
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

                # If ignore_suffix is True and we're at the last row, insertion cost is 0 (no penalty for suffix in long string)
                ins_cost = 0 if ignore_suffix and row_i == s1_len else ins_cost

                cell_value = min( # save min full cost for this step
                    matrix[row_i - 1, cell_i] + del_cost,    # deletion
                    matrix[row_i, cell_i - 1] + ins_cost,    # insertion
                    matrix[row_i - 1, cell_i - 1] + sub_cost # substitution
                )

            matrix[row_i, cell_i] = cell_value = min(cell_value, 1e6)
            # logger.debug(f"Cell ({row_i}={char1}, {cell_i}={char2}) value: {cell_value}")

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
    logger.debug(f"Returning matrix of size {matrix.shape} for {s1=} {s2=}")
    return matrix

class LevenshteinDistanceMode(Enum):
    LONG = auto()
    SHORT = auto()
    SUBSTRING = auto()

def levenshtein_distance(
    s1: str,
    s2: str,
    max_distance: float | None = None,
    narrow: bool = False,
    mode: LevenshteinDistanceMode = LevenshteinDistanceMode.LONG,
    proximity_graph: ProximityGraph = {}
) -> tuple[Span, float]:
    '''
    Returns the length of a substr in the longer string (s2 if equal) for the best levenshtein match with the shorter string, and the best distance for that length.
    Modes:
        - LONG: matches two strings / full distance, max is the len of the longer string
        - SHORT: matches shorter string inside the longer one / best distance to make the shorter string match the longer string substring of the same length (square matrix), better for default edit operation cost
        - SUBSTRING: returns the best matched common substring between the longer and the shorter strings - better with custom float or 0 edit operation costs
    '''
    s1, s2 = (s1, s2) if len(s1) <= len(s2) else (s2, s1) # make sure s2 is longer than s1
    matrix = levenshtein_matrix(s1, s2, max_distance, narrow, proximity_graph)
    best_start = 0

    match mode:
        case LevenshteinDistanceMode.LONG:
            best_end = len(s2) # match of both full-length  s1 and s2
            best_distance = float(matrix[-1, best_end])
        case LevenshteinDistanceMode.SHORT:
            best_end = len(s1) # full length of s1, and partial s2? Should look for min instead? Check short vs substring
            best_distance = float(matrix[-1, best_end])
        case LevenshteinDistanceMode.SUBSTRING:
            best_end = int(np.argmin(matrix[-1, :])) # min in the last row - the best common span between full s1 and partial s2 (cuts the trailing part)
            best_distance_for_end = float(matrix[-1, best_end])
            logger.debug(f'{best_end=} {best_distance_for_end=}')

            # now cut the leading part
            reverse_matrix = levenshtein_matrix(
                s1[::-1],
                s2[best_end-1::-1], # same as s2[:best_end][::-1]
                max_distance,
                narrow,
                proximity_graph
            )
            best_start = int(np.argmin(reverse_matrix[-1, ::-1])) # :-1 to unreverse the matrix and get a correct index
            reverse_full_distance = float(reverse_matrix[-1, -1])
            reverse_best_distance = float(reverse_matrix[-1, -(best_start + 1)]) # +1 is just to make negative index work
            reverse_preserved_distance = reverse_full_distance - reverse_best_distance
            best_distance = best_distance_for_end - reverse_preserved_distance
            logger.debug(f"{reverse_full_distance=} {reverse_best_distance=} {reverse_preserved_distance=}")
            logger.debug(f'{s2=} {s2[best_end-1::-1]=}')
            logger.debug(f"{best_start=} {best_end=} -> {s2[best_start:best_end]}")
    logger.debug(f"Best span with mode {mode}: {best_start, best_end}; Distance: {best_distance}")
    if best_start >= best_end:
        logger.debug("Negative span, returning full mismatch")
        return Span.zero, len(s2)
    return Span(best_start, best_end), float(best_distance)

def levenshtein_similarity(
    s1: str,
    s2: str,
    min_similarity: float = 0,
    narrow: bool = False,
    mode: LevenshteinDistanceMode = LevenshteinDistanceMode.LONG,
    proximity_graph: ProximityGraph = {}
) -> tuple[Span, float]:
    '''
    Computes the similarity between two strings using the Levenshtein distance. Output: 0...1 where 1 indicates perfect similarity and 0 indicates perfect mismatch. The length of s1 is used to calculate the maximum possible distance. Returns the best length of s2 to maximally match s1, and the similarity score.
    '''
    tolerance = 1 - min_similarity
    max_total_distance = max(len(s1), len(s2)) if mode == LevenshteinDistanceMode.LONG else min(len(s1), len(s2))
    max_allowed_distance = round(max_total_distance * tolerance)
    span, distance = levenshtein_distance(s1, s2, max_allowed_distance, narrow, mode=mode, proximity_graph=proximity_graph)
    similarity = 1 - distance / span.length if span else 0.0
    logger.debug(f"Similarity: {similarity:.2f}")
    return span, similarity

def levenshtein_match(
    s1: str,
    s2: str,
    min_similarity: float,
    narrow: bool = False,
    mode: LevenshteinDistanceMode = LevenshteinDistanceMode.LONG,
    proximity_graph: ProximityGraph = {}
) -> tuple[Span, bool]:
    '''
    Checks if two strings are similar enough based on the Levenshtein distance. Returns the best length of s2 to maximally match s1, and whether it's a match. Length value is only meaningful when the match is true.
    '''
    span, similarity = levenshtein_similarity(s1, s2, min_similarity, narrow, mode=mode, proximity_graph=proximity_graph)
    logger.debug(f"Match: {similarity >= min_similarity} ({similarity=:.2f} {min_similarity=})")
    return span, similarity >= min_similarity

def levenshtein_substrings_search(
    query: str,
    string: str,
    min_similarity: float,
    mode=LevenshteinDistanceMode.LONG,
    proximity_graph: ProximityGraph = {}
) -> Generator[Span, None, None]:
    '''
    Searches substrings similar to `query` in `string`. Weighted by similarity, optimized with early exists, spaces are skipped. min_similarity=0.9 means not less than 90% of strings matches.
    '''

    if not query or not string:
        return

    query = query.replace(' ', '')
    string = string.strip()

    # iterate over each candidate substring of `string` (sliding window)
    # TODO: iterate words instead of chars?
    i = -1
    while i < len(string)-1:
        i += 1
        if string[i] == ' ':
            # string with leading space and without are the same, so we can skip it
            continue

        span, is_match = levenshtein_match(query, string[i:], min_similarity, mode=mode, proximity_graph=proximity_graph)
        if is_match:
            assert span
            yield Span(i+span.start, i + span.end)
            i += max(0, span.end) # skip matched substring;
            # TODO: review cases of overlapping improving or degrading results
            # TODO: cutting the left part of the string can give better results
            # TODO: right part isn't cutting well too
        break

if __name__ == '__main__':

    logging.basicConfig()
    logger.setLevel(logging.DEBUG)

    # s1 = 'abcl n k n p k'
    # s2 = 'abclnknpk sit amet'
    # s1 = 'abcl n p n k zzz'
    # s1 = 'abcl n p n k'
    # s2 = 'abclnknpk sit amet'
    # s1 = 'Facebookeeee'
    # s2 = 'google'
    # s1 = 'google'
    # s2 = 'Facebookeeee'
    # s1 = 'flaw'
    # s2 = 'lawn'
    # s1 = 'sunday'
    # s2 = 'saturday'
    # s1 = 'elephant'
    # s2 = 'relevant'
    # s1 = 'sitting'[::-1]
    # s2 = 'kitten'[::-1]
    # s1 = 'sunday'
    # s2 = 'saturday'
    # s1 = 'sunday'[::-1]
    # s2 = 'saturday'[::-1]
    # s1 = 'abc'
    # s2 = 'abcyz'
    # s2 = 'xabcyz'
    # s1 = 'cat'
    # s2 = 'cat sat'
    # s2 = 'the cat sat'
    s1 = 'def'
    s2 = 'abcdefghj'
    # s1 = 'abcdefghj'
    # s2 = 'def'
    narrow=False
    proximity_graph={
        ' ': {'-': 0.0}, # space removed from s1
        '-': {' ': 0} # space inserted in s1
    }
    ignore_prefix = True # does great job
    ignore_suffix = True # looks like over removing distance

    dp = levenshtein_matrix(
        s1=s1,
        s2=s2,
        narrow=narrow,
        proximity_graph=proximity_graph,
        ignore_prefix=ignore_prefix,
        ignore_suffix=ignore_suffix
    )
    rdp = levenshtein_matrix(
        s1=s1[::-1],
        s2=s2[::-1],
        narrow=narrow,
        proximity_graph=proximity_graph,
        ignore_prefix=ignore_prefix,
        ignore_suffix=ignore_suffix
    )

    # print(dp.shape)
    # dp[-1, 7] = 99

    # Plot:

    import matplotlib.pyplot as plt
    import numpy as np

    def plot(dp, s1, s2):
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
        plt.colorbar(cax, ax=ax)
        plt.tight_layout()

    plot(rdp, s1[::-1], s2[::-1])
    plot(dp, s1, s2)
    plt.show()  # <- show both at once
