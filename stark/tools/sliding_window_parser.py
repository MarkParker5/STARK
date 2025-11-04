import asyncio
from typing import Awaitable, Callable
from stark.core.patterns.parsing import ParseError
from stark.tools.common.span import Span


def _token_span_to_char_span(tokens: list[str], span: Span, phrase: str) -> Span:
    """Convert a token span (by index) to a character span in the original phrase."""
    if not tokens or not (0 <= span.start <= span.end <= len(tokens)):
        return Span(0, 0)
    # Find the start and end char positions of the tokens in the original phrase
    positions = []
    idx = 0
    for token in tokens:
        # skip leading spaces
        while idx < len(phrase) and phrase[idx].isspace():
            idx += 1
        start = idx
        idx += len(token)
        end = idx
        positions.append((start, end))
    if not positions or span.start >= len(positions) or span.end > len(positions):
        return Span(0, 0)
    char_start = positions[span.start][0]
    char_end = (
        positions[span.end - 1][1]
        if span.end > span.start
        else positions[span.start][0]
    )
    return Span(char_start, char_end)


async def _binary_cookie_trim[T](
    tokens: list[str],
    start: int,
    end: int,
    parser: Callable[[str], Awaitable[T]],
    baseline_value: T,
    phrase: str,
) -> tuple[Span, str, T]:
    """
    Return minimal (char Span, substring, value) such that
    parser(' '.join(tokens[span.start:span.end])) == baseline_value.
    """
    # Binary search for the leftmost index such that tokens[left:end] still parses to baseline_value.
    left = start
    l_low, l_high = start, end - 1
    while l_low <= l_high:
        mid = (l_low + l_high) // 2
        try:
            r = await parser(" ".join(tokens[mid:end]))
        except ParseError:
            r = None
        if r == baseline_value:
            left = mid
            l_low = mid + 1
        else:
            l_high = mid - 1

    # Binary search for the rightmost index such that tokens[left:right] still parses to baseline_value.
    right = end
    r_low, r_high = left + 1, end
    while r_low <= r_high:
        mid = (r_low + r_high) // 2
        try:
            res = await parser(" ".join(tokens[left:mid]))
        except ParseError:
            res = None
        if res == baseline_value:
            right = mid
            r_high = mid - 1
        else:
            r_low = mid + 1
    token_span = Span(left, right)
    char_span = _token_span_to_char_span(tokens, token_span, phrase)
    substr = phrase[char_span.start : char_span.end]
    return char_span, substr, baseline_value


async def sliding_window_parse[T](
    phrase: str,
    parser: Callable[[str], Awaitable[T]],
    min_window: int = 1,
    max_window: int | None = None,
    concurrency: int | None = None,
    find_one: bool = True,
) -> list[tuple[Span, str, T]]:
    tokens: list[str] = phrase.split()
    n: int = len(tokens)
    if n == 0 or parser is None:
        return None
    if max_window is None:
        max_window = n

    if concurrency is not None and concurrency > 0:
        # Use a semaphore to limit concurrency of parser calls.
        sem = asyncio.Semaphore(concurrency)

        async def try_window(i: int, j: int) -> T:
            async with sem:
                try:
                    return await parser(" ".join(tokens[i:j]))
                except ParseError:
                    return None
    else:

        async def try_window(i: int, j: int) -> T:
            try:
                return await parser(" ".join(tokens[i:j]))
            except ParseError:
                return None

    # Slide a window of decreasing size over the tokens, left to right.
    # Try parsing for each window. Once successful, trim to minimal window.
    results: list[tuple[Span, str, T]] = []
    for window_size in range(min(max_window, n), min_window - 1, -1):
        for start in range(0, n - window_size + 1):
            end = start + window_size
            try:
                res = await try_window(start, end)
            except ParseError:
                res = None
            if res is None:
                continue
            char_span, substr, value = await _binary_cookie_trim(
                tokens, start, end, parser, res, phrase
            )
            result = (char_span, substr, value)
            if find_one:
                return [result]
            else:
                results.append(result)
            # TODO: limit next windows left edge to char_span.end

    if results:
        return results

    # If no valid window is found, raise an error.
    raise ParseError(f"No valid window found using parser={parser} in phrase={phrase}")
