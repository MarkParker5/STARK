import re
from dataclasses import dataclass
from typing import Callable, Optional


class UnhandledTagError(ValueError):
    @staticmethod
    def throw(tag: str):
        raise UnhandledTagError(f'Unhandled tag: {tag}')

@dataclass
class Rule:
    pattern: str
    replace: Optional[str] = None
    func: Optional[Callable[[re.Match], str]] = None

alphanumerics = r'A-zА-яЁё0-9'
parameters = r'$:'
specials = r'\(\)\[\]\{\}\.'
any = alphanumerics + parameters + specials

# tags

ALL_UNORDERED = 'slots'
ONE_OR_MORE_UNORDERED = 'slotsone'

rules_list = [
    # NOTE: order matters
    # stark brackets ()[]{} must be processed before any other rules so it doesn't interfere with regexes brackets
    # stark stars must be right after to avoid replacing regex stars

    # one of the list (a|b|c)
    Rule(r'\(((?:.*\|)*.*)\)', r'(?:\1)'),
    # one or none of the list (a|b|c)?, just add '?'; the space after `?` should not be added to avoid double-space requirement

    # none or more of the list, space-splitted {a|b|c}?; the space after `?` should not be added to avoid double-space requirement
    Rule(r'\{((?:.*\|?)*?.*?)\}\?', r'(?:(?:\1)\\s?)*'),

    # one or more of the list, space-splitted {a|b|c}
    Rule(r'\{((?:.*\|?)*?.*?)\}', r'(?:(?:\1)\\s?)+'),

    # double stars **
    Rule(r'\*\*\?', fr'[{alphanumerics}\\s]*'), # `**?` for any few words or none; the space after `?` should not be added to avoid double-space requirement
    Rule(r'\*\*', fr'[{alphanumerics}\\s]+'), # `**` for any few words but at least one

    # single star*
    # allows variable word form (different prefixes, postfixes, suffixes, etc) must "touch" the word (before, after, or in the middle)
    Rule(fr'([^{specials}]|^)\*', fr'\1[{alphanumerics}]*'),

    # (beta) unordered slots - all required; doesn't work well with multiword wildcards
    Rule(fr'<{ALL_UNORDERED}>(.*?)</{ALL_UNORDERED}>', func=lambda m: '(?:' + ''.join(rf'(?=.*\b{x}\b)' for x in m.group(1).split('|')) + '.*)'),

    # (beta) unordered slots - at least one required; doesn't work well with multiword wildcards
    Rule(fr'<{ONE_OR_MORE_UNORDERED}>(.*?)</{ONE_OR_MORE_UNORDERED}>', func=lambda m: '(?:' + ''.join(rf'(?=.*\b{x}\b)?' for x in m.group(1).split('|')) + '.*)'),

    # make sure all tags are handled
    Rule(r'<[^>]+>', func=lambda m: UnhandledTagError.throw(m.group(0)))
]

# handy rule functions for collections

def one_from(*args: str) -> str:
    return '(' + '|'.join(args) + ')'

def one_or_more_from(*args: str) -> str:
    return '{' + '|'.join(args) + '}'

def all_unordered(*args: str) -> str:
    return f'<{ALL_UNORDERED}>' + '|'.join(args) + f'</{ALL_UNORDERED}>'

def one_or_more_unordered(*args: str) -> str:
    return f'<{ONE_OR_MORE_UNORDERED}>' + '|'.join(args) + f'</{ONE_OR_MORE_UNORDERED}>'

# Multiple capturing groups and lookahead draft, might be helpful for better unordered slots impl
# >>> import regex
# >>> p = '(?=one|two)(?:(?<o>one[abcd]*?)|(?<t>two[fghj]*?))+$'
# >>> s = 'oneabtwofjoneaonebonectwotwotwotwotwojjjjjoneaaaa'
# >>> regex.search(p, s).capturesdict()
# {
# 'o': ['oneab', 'onea', 'oneb', 'onec', 'oneaaaa'],
# 't': ['twofj', 'two', 'two', 'two', 'two', 'twojjjjj']
# }
# >>> p2 = '(?=(?<o>one[abcd]*?)|(?<t>two[fghj]*?))(?:(?<o>one[abcd]*?)|(?<t>two[fghj]*?))+$'
# >>> s2 = 'oneaatwojj'
# >>> regex.search(p2, s2).capturesdict()
# {'o': ['one', 'oneaa'], 't': ['twojj']}
