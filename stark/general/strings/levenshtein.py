from typing import Generator
import numpy as np


def levenshtein(query: str, string: str, threshold: float) -> Generator[str, None, None]:
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
            yield suggested_substring.strip()
