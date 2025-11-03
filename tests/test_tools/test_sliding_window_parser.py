import pytest
from stark.tools.sliding_window_parser import _binary_cookie_trim, sliding_window_parse
from stark.tools.common.span import Span


async def date_parser(text: str):
    """
    Simulates a date parser:
    - Returns ("date", value) if text matches a known date pattern.
    - Handles partial and ambiguous matches.
    """
    text = text.lower().strip()
    if text in {"september 5", "5 september", "september 5th"}:
        return ("date", "2024-09-05")
    if text == "september":
        return ("month", "09")
    if text in {"5", "5th"}:
        return ("day", "05")
    if text in {"6", "6th"}:
        return ("day", "06")
    return None


async def name_parser(text: str):
    """
    Simulates a name parser:
    - Returns ("name", value) if text matches a known name.
    """
    text = text.strip()
    if text.lower() == "john doe":
        return ("name", "John Doe")
    if text.lower() == "john":
        return ("name", "John")
    return None


async def slot_parser(text: str):
    """
    Simulates a slot parser for 'reminder' phrases.
    """
    text = text.lower().strip()
    if text.startswith("remind me to "):
        return ("reminder", text[12:].lstrip())
    return None


# --- _binary_cookie_trim NER tests ---


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "tokens, start, end, baseline_value, parser, expected_span, expected_substr, expected_value",
    [
        # Exact date match
        (
            "remind me to call mom on september 5".split(),
            6,
            8,
            ("date", "2024-09-05"),
            date_parser,
            Span(6, 8),
            "september 5",
            ("date", "2024-09-05"),
        ),
        # Partial match (month only)
        (
            "remind me to call mom on september".split(),
            6,
            7,
            ("month", "09"),
            date_parser,
            Span(6, 7),
            "september",
            ("month", "09"),
        ),
        # Partial match (day only)
        (
            "remind me to call mom on 5".split(),
            6,
            7,
            ("day", "05"),
            date_parser,
            Span(6, 7),
            "5",
            ("day", "05"),
        ),
        # Name match
        (
            "meet john doe at the park".split(),
            1,
            3,
            ("name", "John Doe"),
            name_parser,
            Span(1, 3),
            "john doe",
            ("name", "John Doe"),
        ),
        # Name partial match
        (
            "meet john at the park".split(),
            1,
            2,
            ("name", "John"),
            name_parser,
            Span(1, 2),
            "john",
            ("name", "John"),
        ),
    ],
)
async def test__binary_cookie_trim_ner(
    tokens,
    start,
    end,
    baseline_value,
    parser,
    expected_span,
    expected_substr,
    expected_value,
):
    span, substr, value = await _binary_cookie_trim(
        tokens, start, end, parser, baseline_value
    )
    print(
        f"\n[Trim NER] tokens={tokens}, span={span}, substr='{substr}', value={value}"
    )
    assert span == expected_span
    assert substr == expected_substr
    assert value == expected_value


# --- sliding_window_parse NER tests ---


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "phrase, parser, min_window, max_window, find_one, expected_results",
    [
        # Simple date extraction
        (
            "remind me to call mom on september 5",
            date_parser,
            1,
            None,
            True,
            [(Span(6, 8), "september 5", ("date", "2024-09-05"))],
        ),
        # Partial date (month only)
        (
            "remind me to call mom on september",
            date_parser,
            1,
            None,
            True,
            [(Span(6, 7), "september", ("month", "09"))],
        ),
        # Partial date (day only)
        (
            "remind me to call mom on 5",
            date_parser,
            1,
            None,
            True,
            [(Span(6, 7), "5", ("day", "05"))],
        ),
        # Name extraction
        (
            "meet john doe at the park",
            name_parser,
            1,
            None,
            True,
            [(Span(1, 3), "john doe", ("name", "John Doe"))],
        ),
        # Name partial
        (
            "meet john at the park",
            name_parser,
            1,
            None,
            True,
            [(Span(1, 2), "john", ("name", "John"))],
        ),
        # Multiple entities: name and date
        (
            "meet john doe on september 5",
            None,  # will be replaced below with async def
            1,
            None,
            False,
            [
                (Span(1, 3), "john doe", ("name", "John Doe")),
                (Span(4, 6), "september 5", ("date", "2024-09-05")),
            ],
        ),
        # Overlapping/adjacent dates
        (
            "remind me on september 5 and 6",
            date_parser,
            1,
            None,
            False,
            [
                (Span(3, 5), "september 5", ("date", "2024-09-05")),
                (
                    Span(6, 7),
                    "6",
                    ("day", "06"),
                ),
            ],
        ),
        # No match
        ("remind me to call mom tomorrow", date_parser, 1, None, True, []),
        # Slot parser
        (
            "remind me to buy milk",
            slot_parser,
            1,
            None,
            True,
            [(Span(0, 5), "remind me to buy milk", ("reminder", "buy milk"))],
        ),
    ],
)
async def test_sliding_window_parse_ner(
    phrase, parser, min_window, max_window, find_one, expected_results
):
    # If parser is None, use the multi-entity async_parser for that case
    if parser is None and "meet john doe on september 5" in phrase:

        async def async_parser(s):
            res = await date_parser(s)
            if res:
                return res
            return await name_parser(s)
    else:
        import inspect

        if inspect.iscoroutinefunction(parser):
            async_parser = parser
        else:

            async def async_parser(s):
                return parser(s)

    try:
        results = await sliding_window_parse(
            phrase,
            parser=async_parser,
            min_window=min_window,
            max_window=max_window,
            concurrency=None,
            find_one=find_one,
        )
    except Exception:
        results = []
    print(f"\n[Smart NER] phrase='{phrase}'")
    if not expected_results:
        assert not results or results == [], f"Expected no results, got {results}"
        print("  No entities found.")
    else:
        assert isinstance(results, list)
        # Check that all expected results are included in the results (order/extra partials allowed)
        for exp_span, exp_substr, exp_value in expected_results:
            found = False
            for span, substr, value in results:
                if span == exp_span and substr == exp_substr and value == exp_value:
                    found = True
                    print(
                        f"  Found expected entity: span={span}, substr='{substr}', value={value}"
                    )
                    break
            assert found, (
                f"Expected entity (span={exp_span}, substr='{exp_substr}', value={exp_value}) not found in results: {results}"
            )
