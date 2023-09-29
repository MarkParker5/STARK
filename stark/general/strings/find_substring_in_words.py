
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
    
def startswith_endof(str1: str, str2: str) -> str:
    if str1.startswith(str2):
        return str2
    return ''
