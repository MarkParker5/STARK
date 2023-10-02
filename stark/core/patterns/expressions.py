alphanumerics = r'A-zА-яЁё0-9'
specials = r'\(\)\[\]\{\}'
any = alphanumerics + specials

dictionary = [
    #   one of the list (a|b|c)
    (r'\(((?:.*\|)*.*)\)', r'(?:\1)'),
    
    #   one or more of the list, space-splitted {a|b|c}
    (r'\{((?:.*\|?)*?.*?)\}', r'(?:(?:\1)\\s?)+'),
    
    #   stars *
    (r' ?\*\* ?', fr' ?[{alphanumerics}\\s]* ?'), # ** for any few words
    (fr' ?([^{specials}]|^)\* ?', fr' ?[{alphanumerics}]* ?'), # * for any word
]
