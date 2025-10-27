# cython: boundscheck=False, cdivision=True, initializedcheck=False, language_level=3, wraparound=False
import numpy as np
cimport numpy as np
from stark.tools.common.span import Span


# --- Calculus ---

cdef double[:] fordward_fill(double[:] arr, bint backward):
    cdef Py_ssize_t i, n = arr.shape[0]
    cdef double val, last_value = 0
    cdef double[::1] out = np.empty(n, dtype=np.float64)
    if backward:
        for i in range(n):
            val = arr[i]
            if val == 0:
                out[i] = last_value
            else:
                out[i] = val
                last_value = val
    else:
        for i in range(n-1, -1, -1):
            val = arr[i]
            if val == 0:
                out[i] = last_value
            else:
                out[i] = val
                last_value = val
    return out

cdef np.ndarray extremums(double[:] arr, bint last, bint minima):
    cdef np.ndarray diff_sign = np.sign(np.diff(arr))
    cdef double[:] diff_sign_mv = diff_sign
    diff_sign_mv = fordward_fill(diff_sign_mv, last)
    diff_sign = np.append(diff_sign, 1 if minima else -1)
    cdef np.ndarray diff2 = np.diff(diff_sign)
    return np.argwhere(diff2 > 0 if minima else diff2 < 0).flatten()

cdef int pathtrack_start_column(
    np.ndarray matrix, int rows, int columns, int end_column
):
    cdef int r = rows
    cdef int c = end_column if end_column != -1 else columns
    cdef double deletion, substitution, insertion, minimal
    while r > 0:
        deletion = matrix[r - 1][c]
        substitution = matrix[r - 1][c - 1]
        insertion = matrix[r][c - 1]
        minimal = min(deletion, substitution, insertion)
        if minimal == substitution:
            r -= 1
            c -= 1
        elif minimal == insertion:
            c -= 1
        elif minimal == deletion:
            r -= 1
    return c

# --- Models ---

cdef class LevenshteinParams:
    cdef public str s1, s2
    cdef public double max_distance
    cdef public dict proximity_graph
    cdef public bint ignore_prefix, ignore_suffix, narrow, early_return, lower
    cdef double[:, :] prox
    cdef Py_ssize_t prox_shape0
    cdef Py_ssize_t prox_shape1
    cdef public int last_r, last_c, s1_len, s2_len

    def __init__(self, s1, s2, proximity_graph=None, max_distance=1e6, ignore_prefix=False, ignore_suffix=False, narrow=False, early_return=True, lower=True):

        # make sure s1 isn't longer than s2
        s1, s2 = (s1, s2) if len(s1) <= len(s2) else (s2, s1)

        self.narrow = False

        if lower:
            self.s1 = s1.lower()
            self.s2 = s2.lower()
        else:
            self.s1 = s1
            self.s2 = s2

        self.last_r = self.s1_len = len(s1)
        self.last_c = self.s2_len = len(s2)

        if proximity_graph is None:
            self.proximity_graph = {}
        else:
            self.proximity_graph = proximity_graph

        self.max_distance = max_distance
        self.ignore_prefix = ignore_prefix
        self.ignore_suffix = ignore_suffix
        self.narrow = narrow
        self.early_return = early_return
        self.lower = lower
        self._build_proximity()

    cdef void _build_proximity(self):
        cdef int MAX_CHARS = 128
        cdef int i
        self.prox = np.full((MAX_CHARS, MAX_CHARS), 1.0, dtype=np.float64)
        self.prox_shape0 = self.prox.shape[0]
        self.prox_shape1 = self.prox.shape[1]
        for c1, inner in self.proximity_graph.items():
            i = ord(c1)
            for c2, val in inner.items():
                self.prox[i, ord(c2)] = val

    cdef inline double proximity(self, int c1, int c2) except *:
        if c1 < self.prox_shape0 and c2 < self.prox_shape1:
            return self.prox[c1, c2]
        return 1.0

    # cdef inline double proximity(self, char c1, char c2) except *:
    #     cdef int i1 = ord(c1)
    #     cdef int i2 = ord(c2)
    #     if i1 < self.prox_shape0 and i2 < self.prox_shape1:
    #         return self.prox[i1, i2]
    #     return 1.0

# --- Main Levenshtein functions ---

cdef int none = ord('-')

cpdef np.ndarray levenshtein_matrix(LevenshteinParams p):
    cdef int s1_len = p.s1_len
    cdef int s2_len = p.s2_len
    cdef np.ndarray[np.int32_t, ndim=1] s1 = np.array([ord(c) for c in p.s1], dtype=np.int32)
    cdef np.ndarray[np.int32_t, ndim=1] s2 = np.array([ord(c) for c in p.s2], dtype=np.int32)

    cdef int abs_max_distance = min(s1_len, s2_len) if p.narrow else max(s1_len, s2_len)
    cdef double max_distance = p.max_distance if p.max_distance is not None else abs_max_distance

    matrix_np = np.full((s1_len + 1, s2_len + 1), 1e6, dtype=np.float64)
    cdef double[:, :] matrix = matrix_np # use memoryview for faster access in the loop
    cdef object proximity = p.proximity # save attribute lookup overhead

    s1_inserts = [0.0] + [proximity(none, code) for code in s1]
    s2_inserts = [0.0] + [proximity(none, code) for code in s2]
    matrix_np[:, 0] = np.cumsum(np.array(s1_inserts))
    matrix_np[0, :] = 0 if p.ignore_prefix else np.cumsum(np.array(s2_inserts))
    cdef int best_column = 0

    # logger.debug(f"Building levenshtein matrix for '{p.s1=}' and '{p.s2=}'")

    cdef int row_i, cell_i, start_column
    cdef double cell_value, del_cost, ins_cost, sub_cost

    for row_i in range(1, s1_len + 1):
        char1 = s1[row_i - 1]
        del_cost = proximity(char1, none)
        start_column = 1
        best_column = 0
        # start_column = max(1, best_column - 1) if p.narrow else 1
        for cell_i in range(start_column, s2_len + 1):
            char2 = s2[cell_i - 1]
            if char1 == char2 and matrix[row_i - 1, cell_i - 1] != 1e6:
                cell_value = matrix[row_i - 1, cell_i - 1]
            else:
                ins_cost = proximity(none, char2)
                sub_cost = proximity(char1, char2)
                if row_i == s1_len and p.ignore_suffix:
                    ins_cost = 0.0
                cell_value = min(
                    1e6, # so (1e6 + cost) does not create fake extremums
                    matrix[row_i - 1, cell_i] + del_cost,
                    matrix[row_i, cell_i - 1] + ins_cost,
                    matrix[row_i - 1, cell_i - 1] + sub_cost,
                )
            matrix[row_i, cell_i] = cell_value
            if cell_value < matrix[row_i, best_column]:
                  best_column = cell_i
            # if p.narrow:
            #     if (
            #         cell_value > matrix[row_i, cell_i - 1]
            #         and row_i != s1_len
            #     ):
            #         # logger.debug(...)
            #         break
        if (
            p.early_return and matrix[row_i, best_column] > max_distance
        ):
            # logger.debug(...)
            return matrix_np
    # logger.debug(...)
    return matrix_np

# Wrappers

cpdef double levenshtein_distance(LevenshteinParams p):
    matrix = levenshtein_matrix(p)
    return float(matrix[p.last_r, p.last_c])

cpdef double levenshtein_similarity(double threshold, LevenshteinParams p):
    cdef int abs_max_distance = max(len(p.s1), len(p.s2))
    p.max_distance = abs_max_distance * (1 - threshold)
    cdef double distance = levenshtein_distance(p)
    return 1 - distance / abs_max_distance

cpdef bint levenshtein_match(double threshold, LevenshteinParams p):
    return levenshtein_similarity(threshold, p) >= threshold

# Substring

cdef double matrix_last_row_value(double[:, :] matrix, int c, int last_r):
    return matrix[last_r, c]

def tuple_start(result):
    return result[0].start

cpdef list levenshtein_distance_substring(LevenshteinParams p):
    matrix = levenshtein_matrix(p)
    ends = extremums(matrix[p.last_r, :], 1, 1) + 1
    ends = ends[::-1] # reverse
    result = []
    last_start = 1e6

    # Use functools.partial to bind matrix and last_r
    import functools
    sortkey = functools.partial(matrix_last_row_value, matrix, last_r=p.last_r)
    ends = sorted(ends, key=sortkey)

    for end in ends:
        if end > last_start:
            continue
        start = pathtrack_start_column(matrix, len(p.s1), len(p.s2), end_column=end)
        if start == end:
            continue
        distance = matrix[p.last_r, end]
        result.append((Span(int(start), int(end)), float(distance)))
        last_start = start

    result = sorted(result, key=tuple_start)

    return result

cpdef list levenshtein_similarity_substring(double threshold, LevenshteinParams p):
    cdef double tolerance = 1 - threshold
    cdef int max_total_distance = min(len(p.s1), len(p.s2)) if p.ignore_prefix and p.ignore_suffix else max(len(p.s1), len(p.s2))
    p.max_distance = round(max_total_distance * tolerance)
    return [(span, (1 - distance / span.length if span else 0.0))
            for span, distance in levenshtein_distance_substring(p)]

cpdef list levenshtein_search_substring(double threshold, LevenshteinParams p):
    return [(span, similarity)
            for span, similarity in levenshtein_similarity_substring(threshold, p)
            if similarity >= threshold]
