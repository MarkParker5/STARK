from itertools import groupby
import string
from typing import Generator

from stark.tools.common.span import Span


def split_indices(s: str, sep: str = string.whitespace) -> Generator[Span, None, None]:
    # assert len(sep) == 1, "Separator must be a single character"
    p = 0
    for k, g in groupby(s, lambda x: x in sep):
        q = p + sum(1 for _ in g)
        if not k:
            yield Span(p, q)
        p = q


def find_substring_in_words_map(substr: str, words: list[str]) -> list[list[int]]:
    remaining = substr.strip()

    to_return_candidates: list[int] = []
    to_return: list[list[int]] = []

    for i, word in enumerate(words):
        if remaining in word:
            remaining = ""
            to_return_candidates.append(i)

        elif interception := endswith_startof(word, remaining):
            remaining = remaining[len(interception) :].strip()
            to_return_candidates.append(i)

        elif word.startswith(remaining):
            remaining = ""
            to_return_candidates.append(i)

        else:
            remaining = substr.strip()
            to_return_candidates = []

        if not remaining:
            remaining = substr.strip()
            to_return.append(to_return_candidates)
            to_return_candidates = []

    return to_return


def endswith_startof(s1: str, s2: str) -> str:
    i, j = 0, 0
    n1, n2 = len(s1), len(s2)

    while i < n1:
        j = 0
        temp = ""
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

    return ""
