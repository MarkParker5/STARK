# Sliding Window Parser

## Overview

`sliding_window_parser` helps you find and extract parameters from free text using a parser function even if it doesn't parse the entire input or returns just the value without the substring or the span.
It slides through the sentence with growing/shrinking substring windows and tests each span until finds a suitable match.

### Basic Usage

```python
from stark.tools.sliding_window_parser import sliding_window_parse, Span

async def date_parser(text: str):
    if text.lower() in {"september 5", "5 september"}:
        return ("date", "2024-09-05")
    if text.lower() == "september":
        return ("month", "09")
    return None

result = await sliding_window_parse(
    "remind me to call mom on september 5",
    parser=date_parser,
)
print(result) # [(Span(27, 39), "september 5", ("date", "2024-09-05"))]
```

### Parameters

```
async def sliding_window_parse(
    phrase: str,
    parser: Callable[[str], Awaitable[T]],
    min_window: int = 1,
    max_window: int | None = None,
    concurrency: int | None = None,
    find_one: bool = True,
) -> list[tuple[Span, str, T]]:

- **phrase** – text to parse
- **parser** – async callable returning a parsed value, `None`, or ParseError
- **min_window / max_window** – window size range in tokens (words)
- **concurrency** – limit parallel parser calls, default is `None` (unlimited)
- **find_one** – stop after first match instead of collecting all

Returns:
        A list of tuples (span, substring, value) for each match, where:
        - span: Span object with character offsets (start, end) in the original phrase
        - substring: the matched substring (phrase[span.start:span.end])
        - value: the value returned by the parser

        If find_one=True, returns a single-item list with the first match (faster, less parser calls).
        If no match is found, raises ParseError, so the list is never empty, meaning result[0] is always safe.
```
