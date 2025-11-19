from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Generator

logger = logging.getLogger(__name__)


@dataclass
class PatternParameter:
    name: str
    group_name: str  # includes tree prefix
    type_name: str
    optional: bool


class Pattern:
    parameters: dict[str, PatternParameter]
    # compiled: str

    _origin: str
    _parameter_regex: re.Pattern

    def __init__(self, origin: str):
        self._origin = origin
        self._parameter_regex = self._get_pattern_parameter_annotation_regex()
        self.parameters = dict(self._get_parameters_annotation_from_pattern())
        self._update_group_name_to_param()

    # processing pattern

    def _get_pattern_parameter_annotation_regex(self) -> re.Pattern:
        # types = '|'.join(Pattern._parameter_types.keys())
        # return re.compile(r'\$(?P<name>[A-z][A-z0-9]*)\:(?P<type>(?:' + types + r'))')
        # do not use types list because it prevents validation of unknown types
        return re.compile(r"\$(?P<name>[A-z][A-z0-9]*)\:(?P<type>[A-z][A-z0-9]*)(?P<optional>\?)?")

    def _get_parameters_annotation_from_pattern(
        self,
    ) -> Generator[tuple[str, PatternParameter], None, None]:
        for match in re.finditer(self._parameter_regex, self._origin):
            arg_name = match.group("name")
            arg_type_name = match.group("type")
            arg_optional = bool(match.group("optional"))

            # reg_type: RegisteredParameterType | None = Pattern._parameter_types.get(
            #     arg_type_name
            # )

            # if not reg_type:
            #     raise NameError(
            #         f'Unknown type: "{arg_type_name}" for parameter: "{arg_name}" in pattern: "{self._origin}"'
            #     )

            yield (
                arg_name,
                PatternParameter(arg_name, arg_name, arg_type_name, arg_optional),
            )

    def _update_group_name_to_param(self):
        self.group_name_to_param = {param.group_name: param for param in self.parameters.values()}

    # dunder methods

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Pattern):
            raise NotImplementedError(f"Can`t compare Pattern with {type(other)}")
        return self._origin == other._origin

    def __repr__(self) -> str:
        return f"<Pattern '{self._origin}'>"
