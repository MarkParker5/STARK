from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..types import Object

    ObjectType = type[Object]

from typing_extensions import NamedTuple


class ParseResult(NamedTuple):
    obj: Object
    substring: str


class ParseError(Exception):
    pass


class ObjectParser:
    async def did_parse(self, obj: Object, from_string: str) -> str:
        """
        This method is called after parsing from string and setting parameters found in pattern.
        You will very rarely, if ever, need to call this method directly.

        Override this method for more complex parsing from string.

        Returns:
            Minimal substring that is required to parse value.

        Raises:
            ParseError: if parsing failed.
        """
        return from_string


async def parse_object(
    object_type: type[Object],
    parser: ObjectParser,
    from_string: str,
    parsed_parameters: dict[str, Object | None] | None = None,
) -> ParseResult:
    obj = object_type(from_string)  # temp/default value, may be overridden by did_parse
    parsed_parameters = parsed_parameters or {}
    assert parsed_parameters.keys() <= {
        p.name for p in object_type.pattern.parameters.values() if not p.optional
    }

    for name in object_type.pattern.parameters:
        value = parsed_parameters[name]
        setattr(obj, name, value)

    substring = await parser.did_parse(obj, from_string)
    substring = await obj.did_parse(substring)

    assert substring.strip(), ValueError(
        f"Parsed substring must not be empty. Object: {obj}, Parser: {parser}"
    )
    assert substring in from_string, ValueError(
        f"Parsed substring must be a part of the original string. There is no {substring} in {from_string}. Object: {obj}, Parser: {parser}"
    )
    assert obj.value is not None, ValueError(
        f"Parsed object {obj} must have a `value` property set in did_parse method. Object: {obj}, Parser: {parser}"
    )

    return ParseResult(obj, substring)
