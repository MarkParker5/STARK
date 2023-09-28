import numpy as np

def levenshtein(query: str, string: str, trashhold: float) -> str | None:
    if not query or not string:
        return None
    
    max_distance = int(max(len(query), len(string)) * trashhold)
    n = len(query)
    m = len(string)
    best_distance = float('inf')
    suggested_substring = None
    
    for i in range(m - n + 1):
        substring = string[i:i + n]
        dp = np.zeros((n + 1, 2), dtype=int)
        dp[:, 0] = np.arange(n + 1)
        
        for j in range(1, n + 1):
            dp[j, 1] = min(
                dp[j - 1, 0] + 1,
                dp[j, 0] + 1,
                dp[j - 1, 1] + (query[j - 1] != substring[j - 1])
            )
        
        distance = dp[-1, 1]
        if distance < best_distance:
            best_distance = distance
            suggested_substring = substring
            
        if best_distance <= max_distance:
            break
    
    if best_distance <= max_distance:
        return suggested_substring
    else:
        return None
