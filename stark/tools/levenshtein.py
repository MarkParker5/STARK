import logging
from dataclasses import dataclass, field

from typing_extensions import Iterable, NamedTuple

logger = logging.getLogger(__name__)

import numpy as np

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

def fordward_fill(arr: Iterable[float], backward: bool = False) -> Iterable[float]:
    arr = list(arr)
    enumerated = enumerate(arr)
    if not backward: # if first
        enumerated = list(enumerated)[::-1] # fill from end to start
    last_value = 0
    for i, val in enumerated:
        if val == 0:
            arr[i] = last_value
        else:
            last_value = val
    return arr

def extremums(arr: list[float], last: bool = False, minima=True) -> Iterable[int]:
    # first derivative sign - track growth
    diff_sign = np.sign(np.diff(arr))
    # remove plateaus by forward-filling zeros with the last non-zero value to highlight extremes
    diff_sign = fordward_fill(diff_sign, last)
    # plot_chart(diff_sign, s2, 'Diff filled')
    # second derivative - detect changes in growth direction - concavity
    diff2 = np.diff(diff_sign)
    return np.argwhere(diff2 > 0 if minima else diff2 < 0).flatten() # return indices of up/down concave extremes

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

@dataclass
class LevenshteinParams:
    s1: str
    s2: str
    max_distance: float | None = None
    proximity_graph: ProximityGraph = field(default_factory=dict)
    ignore_prefix: bool = False
    ignore_suffix: bool = False
    narrow: bool = False

def levenshtein_matrix(params: LevenshteinParams) -> np.ndarray:
    '''
    Calculates the Levenshtein distance between two strings s1 and s2.
    Max distance stops the calculations early if the distance exceeds the max_distance for better performance.
    Narrow mode minimizes the number of operations, limits max distance to the smaller of the two strings; calculates "substring" match instead of full string match.
    Proximity graph allows tweaking the cost of operations for any character (default cost is 1), for example, based on phonetic similarity, keyboard proximity, char aliases, costless whitespaces, etc.
    s1 is rows, s2 is columns.
    If ignore_prefix is True, there is no penalty for prefix mismatches in s1 (like substring matching).
    If ignore_suffix is True, there is no penalty for suffix mismatches in s1 (like substring matching).
    '''

    p = params
    p.narrow = False # TODO: review implementation, produces wrong results
    s1_len = len(p.s1)
    s2_len = len(p.s2)
    abs_max_distance = min(s1_len, s2_len) if p.narrow else max(s1_len, s2_len)
    max_distance = p.max_distance if p.max_distance is not None else abs_max_distance

    matrix = np.full((s1_len + 1, s2_len + 1), 1e6, dtype=float)
    matrix[:, 0] = np.arange(s1_len + 1)
    matrix[0, :] = 0 if p.ignore_prefix else np.arange(s2_len + 1)
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

                # the last row represents suffix
                ins_cost = 0 if p.ignore_suffix and row_i == s1_len else ins_cost

                cell_value = min( # save min full cost for this step
                    matrix[row_i - 1, cell_i] + del_cost,    # deletion
                    matrix[row_i, cell_i - 1] + ins_cost,    # insertion
                    matrix[row_i - 1, cell_i - 1] + sub_cost # substitution
                )

            matrix[row_i, cell_i] = cell_value = min(cell_value, 1e6)
            # logger.debug(f"Cell ({row_i}={char1}, {cell_i}={char2}) value: {cell_value}")

            if p.narrow: # cut off corners if optimisation param is set
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
    logger.debug(f"Returning matrix of size {matrix.shape} for {p.s1=} {p.s2=}")
    return matrix

def levenshtein_distance(params: LevenshteinParams) -> float:
    ...

def levenshtein_similarity(params: LevenshteinParams) -> float:
    ...

def levenshtein_match(params: LevenshteinParams) -> float:
    ...

def levenshtein_substring_distance(params: LevenshteinParams) -> Iterable[tuple[Span, float]]:
    '''Returns the length of a substr in the longer string (s2 if equal) for the best levenshtein match with the shorter string, and the best distance for that length.'''
    p = params
    p.s1, p.s2 = (p.s1, p.s2) if len(p.s1) <= len(p.s2) else (p.s2, p.s1) # make sure s2 is longer than s1
    matrix = levenshtein_matrix(p)

    p.s1 = p.s1[::-1]
    p.s2 = p.s2[::-1]
    r_matrix = levenshtein_matrix(p)
    r_matrix = np.roll(r_matrix[::-1, ::-1], shift=1, axis=1) # recover s1 direction

    starts = extremums(r_matrix[0, :], last=True, minima=True)
    ends = extremums(matrix[-1, :], last=True, minima=True)
    distances = matrix[-1, ends]
    spans = map(Span, zip(starts, ends))

    return zip(spans, distances)

def levenshtein_similarity(params: LevenshteinParams, min_similarity: float = 0) -> list[tuple[Span, float]]:
    '''
    Computes the similarity between two strings using the Levenshtein distance. Output: 0...1 where 1 indicates perfect similarity and 0 indicates perfect mismatch. The length of s1 is used to calculate the maximum possible distance. Returns the best length of s2 to maximally match s1, and the similarity score.
    '''
    p = params
    tolerance = 1 - min_similarity
    max_total_distance = min(len(p.s1), len(p.s2)) if p.ignore_prefix and p.ignore_suffix else max(len(p.s1), len(p.s2))
    max_allowed_distance = round(max_total_distance * tolerance)
    p.max_distance = max_allowed_distance
    return [(span, (1 - distance / span.length if span else 0.0)) for span, distance in levenshtein_distance(p)]

def levenshtein_search_substring(params: LevenshteinParams, min_similarity: float = 0) -> list[tuple[Span, float]]:
    '''
    Checks if two strings are similar enough based on the Levenshtein distance. Returns the best length of s2 to maximally match s1, and whether it's a match. Length value is only meaningful when the match is true.
    '''
    return [(span, similarity) for span, similarity in levenshtein_similarity(params, min_similarity) if similarity >= min_similarity]

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
        # s1 = 'def'
        # s2 = 'abcdefghj'
        # s1 = 'abcdefghj'
        # s2 = 'def'
        # s1 = 'c a t'
        # s2 = 'abc cat def c at ghj c a t klm'
        # s2 = 'abc cad def bat ghj s a d klm waxt nop'

    s1 = 'hey ho'
    s2 = 'abc he yyo def keyh o ghj heyho klm'

    narrow=False
    proximity_graph={
        ' ': {'-': 0.0}, # space removed from s1
        '-': {' ': 0} # space inserted in s1
    }
    ignore_prefix = True # does great job
    ignore_suffix = False # looks like over removing distance

    dp = levenshtein_matrix(
        LevenshteinParams(
            s1=s1,
            s2=s2,
            narrow=narrow,
            proximity_graph=proximity_graph,
            ignore_prefix=ignore_prefix,
            ignore_suffix=ignore_suffix
        )
    )
    rdp = levenshtein_matrix(
        LevenshteinParams(
            s1=s1[::-1],
            s2=s2[::-1],
            narrow=narrow,
            proximity_graph=proximity_graph,
            ignore_prefix=ignore_prefix,
            ignore_suffix=ignore_suffix
        )
    )

    # print(dp.shape)
    # dp[-1, 7] = 99

    # Plot:

    import matplotlib.pyplot as plt

    def plot(dp, s1, s2, s1_list = None, s2_list = None):
        s1_list = s1_list or ['s1'] + list(s1)
        s2_list = s2_list or ['s2'] + list(s2)
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
        ax.set_xticklabels(s2_list)
        ax.set_yticklabels(s1_list)
        plt.colorbar(cax, ax=ax)
        plt.tight_layout()

    def plot_chart(values: np.ndarray, s2, title: str):
        fig, ax = plt.subplots(figsize=(len(s2) * 0.6, 2.5))
        bars = ax.bar(range(len(values)), values, color=plt.cm.viridis(values / (values.max() or 1)))
        for i, val in enumerate(values):
            weight = 'bold' if val == 0 else 'normal'
            ax.text(i, val, f'{val:.1f}', ha='center', va='bottom',
                    color='white', fontsize=8, fontweight=weight)
        ax.set_xticks(range(len(s2)))
        ax.set_xticklabels(list(s2))
        ax.set_title(title)
        plt.tight_layout()

    rdp = rdp[::-1, ::-1]
    rdp = np.roll(rdp, shift=1, axis=1)
    # sums = np.array([np.add.reduce(dp + rdp),])
    # mins = np.array([np.minimum.reduce(dp + rdp),])
    # sums = np.add.reduce(dp + rdp)
    # mins = np.minimum.reduce(dp + rdp)
    plot(dp, s1, s2)
    plot(rdp, s1, s2)

    # plot(dp + rdp, s1, s2)
    # plot_chart(sums, s2, 'Column sums')
    # plot_chart(mins, s2, 'Column mins')

    # plot_chart(rdp[0, :], s2, 'Start distances')
    # plot_chart(dp[-1, :], s2, 'End distances')

    starts = extremums(rdp[0, :], last=True, minima=True)
    ends = extremums(dp[-1, :], last=True, minima=True)
    distances = dp[-1, ends]
    distances2 = rdp[0, starts] # should be the same
    print(f'{distances}')
    print(f'{distances2}')

    # print(f'{starts=}\n{ends=}')
    spans = list(zip(starts, ends))
    # print(f'{spans=}')
    for span in spans:
        print(span, s2[slice(*span)])

    plt.show()  # <- show both at once
