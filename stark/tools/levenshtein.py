import logging
from dataclasses import dataclass, field

from typing_extensions import Iterable, NamedTuple

logger = logging.getLogger(__name__)

import numpy as np

# --- Notes ---

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

# --- Calculus ---

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

def extremums(arr: list[float], last: bool = False, minima=True) -> np.ndarray[int]:
    # first derivative sign - track growth
    diff_sign = np.sign(np.diff(arr))
    # remove plateaus by forward-filling zeros with the last non-zero value to highlight extremes
    diff_sign = fordward_fill(diff_sign, last)
    # add trailing bound to catch continuous growth case
    diff_sign = np.append(diff_sign, 1 if minima else -1)
    # plot_chart(diff_sign, s2, 'Diff filled')
    # second derivative - detect changes in growth direction - concavity
    diff2 = np.diff(diff_sign)
    return np.argwhere(diff2 > 0 if minima else diff2 < 0).flatten() # return indices of up/down concave extremes

def pathtrack_start_column(matrix: np.ndarray, rows: int, columns: int, end_column: int = -1) -> int:
    r = rows
    c = end_column if end_column != -1 else columns

    # pathtrack to the first row
    logger.debug('starting pathtrack')
    while r > 0:
        logger.debug(f"track r={r}, c={c}; v={matrix[r][c]}")
        deletion = matrix[r-1][c]
        substitution = matrix[r-1][c-1]
        insertion = matrix[r][c-1]
        minimal = min(deletion, substitution, insertion)

        if minimal == substitution:
            r -= 1
            c -= 1
        elif minimal == insertion:
            c -= 1
        elif minimal == deletion:
            r -= 1

    # # continue going left until we reach the end or the local min
    # while c > 0 and matrix[r][c] <= matrix[r][min(c+1, columns)]:
    #     print(f"slide r={r}, c={c}; v={matrix[r][c]}")
    #     c -= 1

    return c

# --- Models ---

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

    @property
    def slice(self) -> slice:
        return slice(self.start, self.end)

type ProximityGraph = dict[str, dict[str, float]]
'''
Directional proximity between characters, used for calculating the cost of substitution, insertion, and deletion.
'''

@dataclass
class LevenshteinParams:
    s1: str
    s2: str
    max_distance: float | None = None
    proximity_graph: ProximityGraph = field(default_factory=dict)
    ignore_prefix: bool = False
    ignore_suffix: bool = False
    narrow: bool = False
    early_return: bool = True

# --- Constants ---

PROX_MED = 0.5
PROX_LOW = 0.25
SIMPLEPHONE_PROXIMITY_GRAPH: ProximityGraph = {
    'w': {'f': PROX_MED, 'a': PROX_LOW, 'y': PROX_LOW},
    'y': {'a': PROX_LOW, 'w': PROX_LOW},
    'a': {'y': PROX_LOW, 'w': PROX_LOW, '-': PROX_LOW}, # '-' for deletion
    'f': {'w': PROX_MED},
    ' ': {'-': 0},
    '-': {'a': PROX_LOW, ' ': 0}, # insertion
}

# --- Levenshtein Implementation ---

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

        char1 = p.s1[row_i - 1]

        # column loop (filling row cells)
        if p.narrow:
            # remove bottom left corner
            # fill next row from the column to the left of the current column by skipping leftmost cells
            start_column = max(1, best_column-1)
        else:
            start_column = 1
        for cell_i in range(start_column, s2_len + 1):

            char2 = p.s2[cell_i - 1]

            if char1 == char2 and matrix[row_i - 1, cell_i - 1] != 1e6: # check for 1e6 in narrow mode
                # full match, no cost added
                cell_value = matrix[row_i - 1, cell_i - 1]

            else: # different characters, calculate additional cost

                # get costs for char edits from the proximity graph
                del_cost = p.proximity_graph.get(char1, {}).get('-', 1.0)
                ins_cost = p.proximity_graph.get('-', {}).get(char2, 1.0)
                sub_cost = p.proximity_graph.get(char1, {}).get(char2, 1.0)

                # the last row represents suffix
                ins_cost = 0 if p.ignore_suffix and row_i == s1_len else ins_cost

                cell_value = min( # save min full cost for this step
                    matrix[row_i - 1, cell_i] + del_cost,    # deletion
                    matrix[row_i, cell_i - 1] + ins_cost,    # insertion
                    matrix[row_i - 1, cell_i - 1] + sub_cost # substitution
                )

            matrix[row_i, cell_i] = cell_value = min(cell_value, 1e6)
            # logger.debug(f"Cell ({row_i}={char1}, {cell_i}={char2}) value: {cell_value}")

            if cell_value < matrix[row_i, cell_i-1]:
                best_column = cell_i
                # logger.debug(f"Best column upd: {best_column=} due to {cell_value=} < {matrix[row_i, cell_i-1]}")
                # logger.debug(np.array2string(matrix, formatter={'float_kind': lambda x: 'x' if np.isclose(x, 1e6) else f"{x:.2f}"}))

            if p.narrow: # remove top right corner
                if (
                    cell_value > matrix[row_i, cell_i-1] # derivative sign is positive -> the prev was the best
                    and row_i != s1_len # don't skip the last row to set the right bottom (-1;-1) cell which represents the full distance
                ):
                    # end this row if the path is already too far
                    logger.debug(f'Skipping row: {matrix[row_i, cell_i]} > {matrix[row_i, cell_i-1]}')
                    break

        # early stop by max distance limit
        if p.early_return and matrix[row_i, best_column] > max_distance: # the best is worse than limit
            logger.debug(np.array2string(matrix, formatter={'float_kind': lambda x: 'x' if np.isclose(x, 1e6) else f"{x:.2f}"}))
            logger.debug(f'Distance limit: {row_i, best_column}={matrix[row_i, best_column]} > {max_distance=}')
            return matrix

    # return fully filled dp
    logger.debug(f"Returning matrix of size {matrix.shape} for {p.s1=} {p.s2=}")
    return matrix

# --- Single Levenshtein wrappers ---

def levenshtein_distance(params: LevenshteinParams) -> float:
    matrix = levenshtein_matrix(params)
    distance = float(matrix[-1, -1])
    logger.debug(f"Distance: {distance:.2f}")
    return distance

def levenshtein_similarity(params: LevenshteinParams, min_similarity: float = 0) -> float:
    abs_max_distance = max(len(params.s1), len(params.s2))
    distance_limit = abs_max_distance * (1 - min_similarity)
    params.max_distance = distance_limit
    distance = levenshtein_distance(params)
    similarity = 1 - distance / abs_max_distance
    logger.debug(f"Similarity: {similarity:.2f} as 1 - {distance:.2f}/{abs_max_distance}")
    return similarity

def levenshtein_match(params: LevenshteinParams, min_similarity: float = 0) -> bool:
    similarity = levenshtein_similarity(params, min_similarity)
    return similarity >= min_similarity

# --- Iterable Levenshtein wrappers ---

def levenshtein_distance_substring(params: LevenshteinParams) -> Iterable[tuple[Span, float]]:
    '''Returns the length of a substr in the longer string (s2 if equal) for the best levenshtein match with the shorter string, and the best distance for that length.'''
    p = params
    p.s1, p.s2 = (p.s1, p.s2) if len(p.s1) <= len(p.s2) else (p.s2, p.s1) # make sure s2 is longer than s1
    matrix = levenshtein_matrix(p)
    ends = extremums(matrix[-1, :], last=True, minima=True) + 1

    result: list[tuple[Span, float]] = []
    last_start = 1e6
    for end in sorted(reversed(ends), key=lambda c: matrix[-1, c]):
        if end > last_start:
            continue
        start = pathtrack_start_column(matrix, len(p.s1), len(p.s2), end_column=end)
        if start==end:
            continue
        distance = matrix[-1, end]
        result.append((Span(int(start), int(end)), float(distance)))
        last_start = start

    logger.debug(f"Span distances: {[(span, distance, p.s2[span.slice]) for span, distance in result]}")
    return sorted(result, key=lambda x: x[0].start)

def levenshtein_similarity_substring(params: LevenshteinParams, min_similarity: float = 0) -> list[tuple[Span, float]]:
    '''
    Computes the similarity between two strings using the Levenshtein distance. Output: 0...1 where 1 indicates perfect similarity and 0 indicates perfect mismatch. The length of s1 is used to calculate the maximum possible distance. Returns the best length of s2 to maximally match s1, and the similarity score.
    '''
    p = params
    tolerance = 1 - min_similarity
    max_total_distance = min(len(p.s1), len(p.s2)) if p.ignore_prefix and p.ignore_suffix else max(len(p.s1), len(p.s2))
    max_allowed_distance = round(max_total_distance * tolerance)
    p.max_distance = max_allowed_distance
    similarities = [(span, (1 - distance / span.length if span else 0.0)) for span, distance in levenshtein_distance_substring(p)]
    logger.debug(f"Similarities: {[(span, score, p.s2[span.slice]) for span, score in similarities]}")
    return similarities

def levenshtein_search_substring(params: LevenshteinParams, min_similarity: float = 0) -> list[tuple[Span, float]]:
    '''
    Checks if two strings are similar enough based on the Levenshtein distance. Returns the best length of s2 to maximally match s1, and whether it's a match. Length value is only meaningful when the match is true.
    '''
    matches = [(span, similarity) for span, similarity in levenshtein_similarity_substring(params, min_similarity) if similarity >= min_similarity]
    logger.debug(f"Matches: {matches}")
    return matches

if __name__ == '__main__':

    logging.basicConfig()
    logger.setLevel(logging.DEBUG)

    # s1 = 'abcl n k n p k'
    # s2 = 'abclnknpk sit amet'
    # s1 = 'abc'
    # s2 = 'xxx abc xxx'
    # s1 = 'abcl n p n k zzz'
    # s1 = 'abcl n p n k'
    # s2 = 'abclnknpk sit amet'
    # s1 = 'Facebookeeee'
    # s2 = 'google'
    # s1 = 'google'
    # s2 = 'Facebookeeee'
    # s1 = 'lawn'
    # s2 = 'flaw'
    # s1 = 'flaw'
    # s2 = 'lawn'
    # s1 = 'sunday'
    # s2 = 'saturday'
    # s1 = 'elephant'
    # s2 = 'relevant'
    # s1 = 'sitting'
    # s2 = 'kitten'
    # s1 = 'sitting'[::-1]
    # s2 = 'kitten'[::-1]
    # s1 = 'sunday'
    # s2 = 'saturday'
    # s1 = 'sunday'[::-1]
    # s2 = 'saturday'[::-1]
    # s1 = 'abc'
    # s2 = 'abcyz'
    # s2 = 'xabcyz'
    s1 = 'cat'
    s2 = 'the bat and sat'
    # s1 = 'google'
    # s2 = 'the doogle and boogle'
    # s2 = 'the bat sat'
    # s2 = 'the cat sat'
    # s2 = 'cat sat'
    # s1 = 'def'
    # s2 = 'abcdefghj'
    # s1 = 'abcdefghj'
    # s2 = 'def'
    # s1 = 'c a t'
    # s2 = 'abc cat def c at ghj c a t klm'
    # s2 = 'abc cad def bat ghj s a d klm waxt nop'

    # s1 = 'hey ho'
    # s2 = 'abc he yyo def keyh o ghj heyho klm'

    narrow=False
    proximity_graph={
        ' ': {'-': 0.01}, # space removed from s1
        '-': {' ': 0.01} # space inserted in s1
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
    # rdp = levenshtein_matrix(
    #     LevenshteinParams(
    #         s1=s1[::-1],
    #         s2=s2[::-1],
    #         narrow=narrow,
    #         proximity_graph=proximity_graph,
    #         ignore_prefix=ignore_prefix,
    #         ignore_suffix=ignore_suffix
    #     )
    # )

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
                ax.text(j, i, f'{val:.2f}', va='center', ha='center', color='white', fontsize=8, fontweight=weight)

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
            ax.text(i, val, f'{val:.2f}', ha='center', va='bottom',
                    color='white', fontsize=8, fontweight=weight)
        ax.set_xticks(range(len(s2)))
        ax.set_xticklabels(list(s2))
        ax.set_title(title)
        plt.tight_layout()

    # rdp = rdp[::-1, ::-1]
    # rdp = np.roll(rdp, shift=1, axis=1)
    # sums = np.array([np.add.reduce(dp + rdp),])
    # mins = np.array([np.minimum.reduce(dp + rdp),])
    # sums = np.add.reduce(dp + rdp)
    # mins = np.minimum.reduce(dp + rdp)
    plot(dp, s1, s2)
    # plot(rdp, s1, s2)

    # plot(dp + rdp, s1, s2)
    # plot_chart(sums, s2, 'Column sums')
    # plot_chart(mins, s2, 'Column mins')

    # plot_chart(rdp[0, :], s2, 'Start distances')
    # plot_chart(dp[-1, :], s2, 'End distances')

    # starts = extremums(rdp[0, :], last=True, minima=True)
    # ends = extremums(dp[-1, :], last=True, minima=True)
    # distances = list(map(float, dp[-1, ends]))
    # distances2 = list(map(float, rdp[0, starts])) # should be the same
    # print(f'{distances=}')
    # print(f'{distances2=}')

    # # print(f'{starts=}\n{ends=}')
    # spans = [(int(a), int(b + 1)) for a, b in list(zip(starts, ends))]
    # print(f'{spans=}')

    # TODO:
        # test with non-symetric multiword string
        # Regroup test cases

    # ends = extremums(dp[-1, :], last=True, minima=True) + 1
    # print(f'{ends=}')
    # starts = [pathtrack_start_column(dp, len(s1), len(s2), end_column=end) for end in ends]
    # spans = [(int(a), int(b + 1)) for a, b in list(zip(starts, ends))]
    # distances = [float(dp[-1, end]) for end in ends]
    # spans = zip(map(int, starts), map(int, ends))
    # matches = zip(spans, distances)

    # matches = []
    # last_start = 1e6
    # for end in sorted(reversed(ends), key=lambda x: dp[-1, x]):
    #     print(f'Processing end={end} with distance={dp[-1, end]}, start would be {pathtrack_start_column(dp, len(s1), len(s2), end_column=end)}')
    #     if end > last_start: # skip overlapping
    #         continue
    #     start = pathtrack_start_column(dp, len(s1), len(s2), end_column=end)
    #     if start==end: # skip empty
    #         continue
    #     distance = dp[-1, end]
    #     matches.append(((int(start), int(end)), float(distance)))
    #     last_start = start

    matches = levenshtein_distance_substring(LevenshteinParams(
        s1=s1,
        s2=s2,
        narrow=narrow,
        proximity_graph=proximity_graph,
        ignore_prefix=ignore_prefix,
        ignore_suffix=ignore_suffix
    ))

    for span, distance in matches:
        print(span, s2[slice(*span)], distance)

    plt.show()  # <- show both at once
