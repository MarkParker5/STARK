import numpy as np

def levenshtein(query: str, string: str, threshold: float) -> str | None:
    if not query or not string:
        return None
    
    query_filtered = query.replace(' ', '')
    max_distance = int(len(query_filtered) * threshold)
    n = len(query)
    m = len(string)
    best_distance = float('inf')
    suggested_substring = None
    
    for i in range(m - n + 1):
        substring = string[i:i + n]
        dp = np.zeros((n + 1, n + 1), dtype=int)
        dp[:, 0] = np.arange(n + 1)
        dp[0, :] = np.arange(n + 1)
        
        for j in range(1, n + 1):
            for k in range(1, n + 1):
                dp[j, k] = dp[j - 1, k - 1] if query[j - 1] == substring[k - 1] else 1e6
                
                if query[j - 1] != ' ' and substring[k - 1] != ' ':
                    dp[j, k] = min(
                        dp[j, k],
                        dp[j - 1, k] + 1,
                        dp[j, k - 1] + 1,
                        dp[j - 1, k - 1] + 1
                    )
                
        distance = dp[-1, -1]
        if distance < best_distance:
            best_distance = distance
            suggested_substring = substring
            
        if best_distance <= max_distance:
            break
    
    if best_distance <= max_distance:
        return suggested_substring
    else:
        return None
