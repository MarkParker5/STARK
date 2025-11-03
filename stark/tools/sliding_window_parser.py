import asyncio
from typing import Awaitable, Callable
from stark.core.patterns.parsing import ParseError
from stark.tools.common.span import Span


async def _binary_cookie_trim[T](
    tokens: list[str],
    start: int,
    end: int,
    parser: Callable[[str], Awaitable[T]],
    baseline_value: T,
) -> tuple[Span, str, T]:
    """
    Return minimal (Span, substring, value) such that
    parser(' '.join(tokens[span.start:span.end])) == baseline_value.
    """
    # Binary search for the leftmost index such that tokens[left:end] still parses to baseline_value.
    left = start
    l_low, l_high = start, end - 1
    while l_low <= l_high:
        mid = (l_low + l_high) // 2
        r = await parser(" ".join(tokens[mid:end]))
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
        res = await parser(" ".join(tokens[left:mid]))
        if res == baseline_value:
            right = mid
            r_high = mid - 1
        else:
            r_low = mid + 1
    span = Span(left, right)
    substr = " ".join(tokens[left:right])
    return span, substr, baseline_value


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
                return await parser(" ".join(tokens[i:j]))
    else:

        async def try_window(i: int, j: int) -> T:
            return await parser(" ".join(tokens[i:j]))

    # Slide a window of decreasing size over the tokens, left to right.
    # Try parsing for each window. Once successful, trim to minimal window.
    results: list[tuple[Span, str, T]] = []
    for window_size in range(min(max_window, n), min_window - 1, -1):
        for start in range(0, n - window_size + 1):
            end = start + window_size
            try:
                res = await try_window(start, end)
            except ParseError:
                continue
            if res is None:
                continue
            # Found a valid window, now trim it to minimal span.
            span, substr, value = await _binary_cookie_trim(
                tokens, start, end, parser, res
            )
            result = (span, substr, value)
            if find_one:
                return [result]
            else:
                results.append(result)
            # TODO: limit next windows left edge to span.end

    if results:
        return results

    # If no valid window is found, raise an error.
    raise ParseError(f"No valid window found using parser={parser} in phrase={phrase}")
