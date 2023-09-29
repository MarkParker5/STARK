import numpy as np

def levenshtein(query: str, string: str, threshold: float) -> str | None: # TODO: return set of all matches
    if not query or not string:
        return None
    
    query_filtered = query.replace(' ', '')
    max_distance = int(round(len(query_filtered) * threshold))
    n = len(query)
    m = len(string)
    best_distance = float('inf')
    suggested_substring = None
    
    for i in range(m - n + 1): # replace slices with better solution and build matrix once (see stackoverflow answer about filling first row with zeros, etc)
        substring = string[i:i + n] # slice doesn't work because string can have unlimited number of spaces
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
        return suggested_substring
    else:
        return None

print('lnknpk', 'lorem ispum ln kn pk sit amet', 0) # must return 'ln kn pk'
