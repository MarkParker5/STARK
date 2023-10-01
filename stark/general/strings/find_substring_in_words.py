def find_substring_in_words(substr: str, words: list[str]) -> list[list[int]]:
    
    remaining = substr.strip()
    
    to_return_candidates: list[int] = []
    to_return: list[list[int]] = []
    
    for i, word in enumerate(words):
        if remaining in word:
            remaining = ''
            to_return_candidates.append(i)
            
        elif interception := startswith_endof(substr, word):
            remaining = remaining[len(interception):].strip()
            to_return_candidates.append(i)
            
        elif word.startswith(remaining):
            remaining = ''
            to_return_candidates.append(i)
            
        else:
            remaining = word.strip()
            to_return_candidates = []
        
        if not remaining:
            remaining = word.strip()
            to_return.append(to_return_candidates)
            to_return_candidates = []
    
    return to_return

def startswith_endof(s1: str, s2: str) -> str:
    i, j = 0, 0
    n1, n2 = len(s1), len(s2)
    
    while i < n1:
        j = 0
        temp = ''
        while j < n2 and i + j < n1:
            if s1[i + j] != s2[j]:
                break
            temp += s1[i + j]
            j += 1
        
        if j == n2:
            return s2

        if j > 0 and i + j == n1:
            return temp
        
        i += 1
    
    return ''
