import logging
from dataclasses import dataclass, field
from typing import TypedDict, Unpack

from typing_extensions import Iterable

logger = logging.getLogger(__name__)

import numpy as np

# --- Calculus ---

def fordward_fill(arr: Iterable[float], backward: bool = False) -> Iterable[float]:
    """
    Forward-fills zeros in an array with the last non-zero value.

    Args:
        arr: Iterable of floats to fill.
        backward: If True, fill from start to end; otherwise, fill from end to start.

    Returns:
        Iterable[float]: The filled array.
    """
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
    """
    Return indices of local minima or maxima in a 1D float array.

    Args:
        arr: Sequence of floats to analyze.
        last: If True, fill plateaus backward; otherwise, forward.
        minima: If True, find minima; if False, find maxima.

    Returns:
        Indices of local minima or maxima as a numpy array of ints.
    """
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
    """
    Tracks the optimal path from the bottom of a Levenshtein matrix to the top row,
    returning the column index where the path starts in the first row.

    Args:
        matrix (np.ndarray): The Levenshtein distance matrix.
        rows (int): Number of rows in the matrix.
        columns (int): Number of columns in the matrix.
        end_column (int, optional): Column to start tracking from. Defaults to last column.

    Returns:
        int: The column index in the first row where the path starts.
    """
    r = rows
    c = end_column if end_column != -1 else columns

    # pathtrack to the first row
    # logger.debug('starting pathtrack')
    while r > 0:
        # logger.debug(f"track r={r}, c={c}; v={matrix[r][c]}")
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

from stark.tools.common.span import Span

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
    lower: bool = True

class LevenshteinParamsDict(TypedDict, total=False):
    """
    Typed dictionary for Levenshtein algorithm parameters.

    Attributes:
        s1: First string to compare.
        s2: Second (larger) string to compare.
        max_distance: Optional maximum allowed distance for early stopping.
        proximity_graph: Mapping of character pairs to operation costs instead of default 1.
        ignore_prefix: If True, ignore mismatches at the start of s1.
        ignore_suffix: If True, ignore mismatches at the end of s1 (not recommended for substring matching).
        narrow: If True, use substring/narrow matching mode. (currently not implemented)
        early_return: If True, stop calculation early if max_distance exceeded.
        lower: If True, compare strings in lowercase.
    """
    s1: str
    s2: str
    max_distance: float | None
    proximity_graph: ProximityGraph
    ignore_prefix: bool
    ignore_suffix: bool
    narrow: bool
    early_return: bool
    lower: bool

# --- Constants ---

PROX_MED = 0.5
PROX_LOW = 0.25
PROX_MIN = 0.01
SIMPLEPHONE_PROXIMITY_GRAPH: ProximityGraph = {
    'w': {'f': PROX_MED, 'a': PROX_LOW, 'y': PROX_LOW},
    'y': {'a': PROX_LOW, 'w': PROX_LOW},
    'a': {'y': PROX_LOW, 'w': PROX_LOW, '-': PROX_LOW}, # '-' for deletion
    'f': {'w': PROX_MED},
    ' ': {'-': 0},
    '-': {'a': PROX_LOW, ' ': 0}, # insertion
}
SKIP_SPACES_GRAPH = {
    ' ': {'-': PROX_MIN},
    '-': {' ': PROX_MIN}
}

# --- Levenshtein Implementation ---

def levenshtein_matrix(params: LevenshteinParams) -> np.ndarray:
    """
    Build the Levenshtein distance matrix for two strings.

    Args:
        params: LevenshteinParams object with all algorithm options.

    Returns:
        np.ndarray: The computed distance matrix.
    """

    p = params
    p.narrow = False # TODO: review implementation, produces wrong results
    if p.lower:
        p.s1 = p.s1.lower()
        p.s2 = p.s2.lower()
    s1_len = len(p.s1)
    s2_len = len(p.s2)
    abs_max_distance = min(s1_len, s2_len) if p.narrow else max(s1_len, s2_len)
    max_distance = p.max_distance if p.max_distance is not None else abs_max_distance

    matrix = np.full((s1_len + 1, s2_len + 1), 1e6, dtype=float)
    s1_inserts = [0] + [p.proximity_graph.get('-', {}).get(char, 1.0) for char in p.s1]
    s2_inserts = [0] + [p.proximity_graph.get('-', {}).get(char, 1.0) for char in p.s2]
    matrix[:, 0] = np.cumsum(np.array(s1_inserts))
    matrix[0, :] = 0 if p.ignore_prefix else np.cumsum(np.array(s2_inserts))
    best_column = 0

    logger.debug(f"Building levenshtein matrix for '{p.s1=}' and '{p.s2=}'")

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

#                 logger.debug(f"({row_i}, {cell_i}) {char1}-{char2}:\
# \t{del_cost=}={matrix[row_i - 1, cell_i] + del_cost},\
# \t{ins_cost=}={matrix[row_i, cell_i - 1] + ins_cost},\
# \t{sub_cost=}={matrix[row_i - 1, cell_i - 1] + sub_cost}; ")

                # the last row represents suffix
                ins_cost = 0 if row_i == s1_len and p.ignore_suffix else ins_cost

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
            # logger.debug(np.array2string(matrix, formatter={'float_kind': lambda x: 'x' if np.isclose(x, 1e6) else f"{x:.2f}"}))
            logger.debug(f'Distance limit: {row_i, best_column}={matrix[row_i, best_column]} > {max_distance=}')
            return matrix

    # return fully filled dp
    logger.debug(f"Returning matrix of size {matrix.shape}")
    return matrix

# --- Single Levenshtein wrappers ---

def levenshtein_distance(**kwargs: Unpack[LevenshteinParamsDict]) -> float:
    """
    Compute the Levenshtein distance between two strings.

    Args:
        kwargs: Parameters for LevenshteinParams.

    Returns:
        float: The Levenshtein distance.
    """
    params = LevenshteinParams(**kwargs)
    matrix = levenshtein_matrix(params)
    distance = float(matrix[-1, -1])
    logger.debug(f"Distance: {distance:.2f}")
    return distance

def levenshtein_similarity(threshold: float = 0, **kwargs: Unpack[LevenshteinParamsDict]) -> float:
    """
    Compute similarity between two strings using Levenshtein distance.

    Args:
        threshold: Minimum similarity threshold.
        kwargs: Parameters for LevenshteinParams.

    Returns:
        float: Similarity score in [0, 1].
    """
    params = LevenshteinParams(**kwargs)
    abs_max_distance = max(len(params.s1), len(params.s2))
    distance_limit = abs_max_distance * (1 - threshold)
    params.max_distance = distance_limit
    distance = levenshtein_distance(**params.__dict__)
    similarity = 1 - distance / abs_max_distance
    logger.debug(f"Similarity: {similarity:.2f} as 1 - {distance:.2f}/{abs_max_distance}")
    return similarity

def levenshtein_match(threshold: float = 0, **kwargs: Unpack[LevenshteinParamsDict]) -> bool:
    """
    Check if two strings match above a similarity threshold.

    Args:
        threshold: Minimum similarity threshold.
        kwargs: Parameters for LevenshteinParams.

    Returns:
        bool: True if similarity >= threshold, else False.
    """
    similarity = levenshtein_similarity(**kwargs, threshold=threshold)
    return similarity >= threshold

# --- Iterable Levenshtein wrappers ---

def levenshtein_distance_substring(**kwargs: Unpack[LevenshteinParamsDict]) -> Iterable[tuple[Span, float]]:
    """
    Find best substring matches and distances for the shorter string in the longer string.

    Args:
        kwargs: Parameters for LevenshteinParams.

    Returns:
        Iterable[tuple[Span, float]]: List of (Span, distance) for best matches.
    """
    p = LevenshteinParams(**kwargs)
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

def levenshtein_similarity_substring(threshold: float = 0,  **kwargs: Unpack[LevenshteinParamsDict]) -> list[tuple[Span, float]]:
    """
    Compute similarity scores for all best substring matches.

    Args:
        threshold: Minimum similarity threshold.
        kwargs: Parameters for LevenshteinParams.

    Returns:
        list[tuple[Span, float]]: List of (Span, similarity) for best matches.
    """
    p = LevenshteinParams(**kwargs)
    tolerance = 1 - threshold
    max_total_distance = min(len(p.s1), len(p.s2)) if p.ignore_prefix and p.ignore_suffix else max(len(p.s1), len(p.s2))
    max_allowed_distance = round(max_total_distance * tolerance)
    p.max_distance = max_allowed_distance
    similarities = [(span, (1 - distance / span.length if span else 0.0)) for span, distance in levenshtein_distance_substring(**p.__dict__)]
    logger.debug(f"Similarities: {[(span, score, p.s2[span.slice]) for span, score in similarities]}")
    return similarities

def levenshtein_search_substring(threshold: float = 0, **kwargs: Unpack[LevenshteinParamsDict]) -> list[tuple[Span, float]]:
    """
    Find substring matches above a similarity threshold.

    Args:
        threshold: Minimum similarity threshold.
        kwargs: Parameters for LevenshteinParams.

    Returns:
        list[tuple[Span, float]]: List of (Span, similarity) for matches above threshold.
    """
    matches = [(span, similarity) for span, similarity in levenshtein_similarity_substring(threshold=threshold, **kwargs) if similarity >= threshold]
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
    # s1 = 'cat'
    # s2 = 'the bat and sat'
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
    s1 = 'SPTFA'
    s2 = 'ASPTAFA'

    narrow=False
    proximity_graph=SIMPLEPHONE_PROXIMITY_GRAPH
    ignore_prefix = False
    ignore_suffix = False # looks like over removing distance info

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
        """
        Plot the Levenshtein distance matrix using matplotlib.

        Args:
            dp: Distance matrix.
            s1: First string.
            s2: Second string.
            s1_list: Optional custom row labels.
            s2_list: Optional custom column labels.
        """
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
        """
        Plot a bar chart for values using matplotlib.

        Args:
            values: Array of values to plot.
            s2: String for x-axis labels.
            title: Chart title.
        """
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
