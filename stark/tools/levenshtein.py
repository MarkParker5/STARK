from typing import Generator

import numpy as np


def levenshtein_distance(a: str, b: str) -> int:
    '''
    Computes the Levenshtein distance between two strings.
    '''

    if not a or not b:
        return max(len(a), len(b))

    n = len(a)
    m = len(b)
    dp = np.full((n + 1, m + 1), 1e6, dtype=int)
    dp[:, 0] = np.arange(n + 1)
    dp[0, :] = np.arange(m + 1)

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                dp[i, j] = dp[i - 1, j - 1]
            else:
                dp[i, j] = min(
                    dp[i - 1, j] + 1,
                    dp[i, j - 1] + 1,
                    dp[i - 1, j - 1] + 1
                )

    return dp[-1, -1]

def levenshtein_similarity(a: str, b: str) -> float:
    '''
    Computes the similarity between two strings using the Levenshtein distance. Output: 0...1 where 1 indicates perfect similarity.
    '''

    if not a or not b:
        return 0.0

    distance = levenshtein_distance(a, b)
    max_length = max(len(a), len(b))

    return 1.0 - distance / max_length

def levenshtein_substrings_search(query: str, string: str, threshold: float) -> Generator[str, None, None]:
    '''
    Searches substrings similar to `query` in `string`.
    '''

    if not query or not string:
        return

    query = query.replace(' ', '')
    string = string.strip()
    max_distance = int(round(len(query) * threshold))
    n = len(query)
    m = len(string)
    # best_distance = float('inf')
    suggested_substring = None

    # Initialize the DP matrix
    dp = np.full((n + 1, n + 1), 1e6, dtype=int)
    dp[:, 0] = np.arange(n + 1)
    dp[0, :] = np.arange(n + 1)

    for i in range(0, m - n + 1):
        if string[i - 1] == ' ':
            continue # string with leading space and without are the same, so we can skip it
        for j in range(1, n + 1):
            # for k in range(1, n + 1):
            k = 0
            dk = 0
            dn = n
            spaces = 0
            while dk < dn:
                dk += 1
                k = dk - spaces

                if i + dk - 1 >= m:
                    break # we reached the end of the string

                if query[j - 1] == string[i + dk - 1]:
                    dp[j, k] = dp[j - 1, k - 1]

                elif string[i + dk - 1] == ' ':
                    dp[j, k] = dp[j - 1, k - 1]
                    dn += 1
                    spaces += 1

                else:
                    dp[j, k] = min(
                        dp[j - 1, k] + 1,
                        dp[j, k - 1] + 1,
                        dp[j - 1, k - 1] + 1
                    )

        distance = dp[-1, -1]
        if distance <= max_distance:
            # best_distance = distance
            suggested_substring = string[i:i + n + spaces]
            yield suggested_substring.strip() # TODO: return indices
