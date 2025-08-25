alphanumerics = r'A-zА-яЁё0-9'
specials = r'\(\)\[\]\{\}'
any = alphanumerics + specials

dictionary = {
    #   one or none of the list - just add `?` (a|b|c)?, the space after `?` should not be added to avoid double-space requirement
    #   one of the list (a|b|c)
    r'\(((?:.*\|)*.*)\)': r'(?:\1)',

    #   none or more of the list, space-splitted {a|b|c}?, the space after `?` should not be added to avoid double-space requirement
    r'\{((?:.*\|?)*?.*?)\}\?': r'(?:(?:\1)\\s?)*',
    #   one or more of the list, space-splitted {a|b|c}
    r'\{((?:.*\|?)*?.*?)\}': r'(?:(?:\1)\\s?)+',

    # double stars **
    r'\*\*\?': fr'[{alphanumerics}\\s]*', # `**?` for any few words or none, the space after `?` should not be added to avoid double-space requirement
    r'\*\*': fr'[{alphanumerics}\\s]+', # `**` for any few words but at least one

    # single star*
    fr'([^{specials}]|^)\*': fr'\1[{alphanumerics}]*', # allows variable word form (different prefixes, postfixes, suffixes, etc) must "touch" the word (before, after, or in the middle)
}

# TODO: greedy (in object patterns) and non-greedy (place fillers) stars
