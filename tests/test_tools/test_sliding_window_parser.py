import pytest

from stark.tools.common.span import Span
from stark.tools.sliding_window_parser import _binary_cookie_trim, sliding_window_parse

# --- Test Parsers ---


async def parser_date_full(s: str):
    if s.lower() in {"september 5", "5 september", "september 5th"}:
        return ("date", "2024-09-05")
    return None


async def parser_date_month(s: str):
    if s.lower() == "september":
        return ("month", "09")
    return None


async def parser_date_day_5(s: str):
    if s.lower() == "5":
        return ("day", "05")
    return None


async def parser_name_full(s: str):
    if s.strip().lower() == "john doe":
        return ("name", "John Doe")
    return None


async def parser_name_partial(s: str):
    if s.strip().lower() == "john":
        return ("name", "John")
    return None


async def parser_date_multi(s: str):
    if s.lower() in {"september 5", "5 september", "september 5th"}:
        return ("date", "2024-09-05")
    if s.lower() == "september":
        return ("month", "09")
    if s.lower() == "5":
        return ("day", "05")
    if s.lower() == "6":
        return ("day", "06")
    return None


async def parser_none(s: str):
    return None


async def parser_slot(s: str):
    if s.lower().strip().startswith("remind me to buy milk"):
        return ("reminder", "buy milk")
    return None


async def parser_name_or_date(s: str):
    if s.strip().lower() == "john doe":
        return ("name", "John Doe")
    if s.lower() in {"september 5", "5 september", "september 5th"}:
        return ("date", "2024-09-05")
    return None


# --- Utility ---


def char_span_for_substr(phrase: str, substr: str) -> Span:
    """Find the first occurrence of substr in phrase and return its char span."""
    start = phrase.find(substr)
    if start == -1:
        raise ValueError(f"Substring '{substr}' not found in phrase '{phrase}'")
    end = start + len(substr)
    return Span(start, end)


# --- _binary_cookie_trim NER tests ---


@pytest.mark.parametrize(
    "phrase, token_start, token_end, baseline_value, parser, expected_substr, expected_value",
    [
        (
            "remind me to call mom on september 5",
            6,
            8,
            ("date", "2024-09-05"),
            parser_date_full,
            "september 5",
            ("date", "2024-09-05"),
        ),
        (
            "remind me to call mom on september",
            6,
            7,
            ("month", "09"),
            parser_date_month,
            "september",
            ("month", "09"),
        ),
        (
            "remind me to call mom on 5",
            6,
            7,
            ("day", "05"),
            parser_date_day_5,
            "5",
            ("day", "05"),
        ),
        (
            "meet john doe at the park",
            1,
            3,
            ("name", "John Doe"),
            parser_name_full,
            "john doe",
            ("name", "John Doe"),
        ),
        (
            "meet john at the park",
            1,
            2,
            ("name", "John"),
            parser_name_partial,
            "john",
            ("name", "John"),
        ),
    ],
)
async def test__binary_cookie_trim_ner(
    phrase,
    token_start,
    token_end,
    baseline_value,
    parser,
    expected_substr,
    expected_value,
):
    tokens = phrase.split()
    char_span, substr, value = await _binary_cookie_trim(tokens, token_start, token_end, parser, baseline_value, phrase)
    expected_span = char_span_for_substr(phrase, expected_substr)
    assert char_span == expected_span
    assert substr == expected_substr
    assert value == expected_value


# --- sliding_window_parse NER tests ---


@pytest.mark.parametrize(
    "phrase, parser, min_window, max_window, find_one, expected_results",
    [
        (
            "remind me to call mom on september 5",
            parser_date_full,
            1,
            None,
            True,
            [("september 5", ("date", "2024-09-05"))],
        ),
        (
            "remind me to call mom on september",
            parser_date_month,
            1,
            None,
            True,
            [("september", ("month", "09"))],
        ),
        (
            "remind me to call mom on 5",
            parser_date_day_5,
            1,
            None,
            True,
            [("5", ("day", "05"))],
        ),
        (
            "meet john doe at the park",
            parser_name_full,
            1,
            None,
            True,
            [("john doe", ("name", "John Doe"))],
        ),
        (
            "meet john at the park",
            parser_name_partial,
            1,
            None,
            True,
            [("john", ("name", "John"))],
        ),
        (
            "meet john doe on september 5",
            parser_name_or_date,
            1,
            None,
            False,
            [
                ("john doe", ("name", "John Doe")),
                ("september 5", ("date", "2024-09-05")),
            ],
        ),
        (
            "remind me on september 5 and 6",
            parser_date_multi,
            1,
            None,
            False,
            [("september 5", ("date", "2024-09-05")), ("6", ("day", "06"))],
        ),
        ("remind me to call mom tomorrow", parser_none, 1, None, True, []),
        (
            "remind me to buy milk",
            parser_slot,
            1,
            None,
            True,
            [("remind me to buy milk", ("reminder", "buy milk"))],
        ),
    ],
)
async def test_sliding_window_parse_ner(phrase, parser, min_window, max_window, find_one, expected_results):
    if not expected_results:
        import pytest

        from stark.core.parsing import ParseError

        with pytest.raises(ParseError):
            await sliding_window_parse(
                phrase,
                parser=parser,
                min_window=min_window,
                max_window=max_window,
                concurrency=None,
                find_one=find_one,
            )
    else:
        results = await sliding_window_parse(
            phrase,
            parser=parser,
            min_window=min_window,
            max_window=max_window,
            concurrency=None,
            find_one=find_one,
        )
        assert isinstance(results, list)
        for expected_substr, expected_value in expected_results:
            found = False
            expected_span = char_span_for_substr(phrase, expected_substr)
            for span, substr, value in results:
                if span == expected_span and substr == expected_substr and value == expected_value:
                    found = True
                    break
            assert found, (
                f"Expected entity (span={expected_span}, substr='{expected_substr}', value={expected_value}) not found in results: {results}"
            )
