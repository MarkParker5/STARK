# from typing import _SpecialGenericAlias
import inspect
import json

from pydantic import BaseModel

from stark import Command, CommandsManager, Pattern
from stark.core.parsing import ObjectType


class CommandInfo(BaseModel):  # TODO: consider moving to Command itself
    name: str
    pattern: str
    declaration: str
    docstring: str

    def as_text(self) -> str:
        return " | ".join(v for v in self.model_dump().values() if v)

    @staticmethod
    def from_command(cmd: Command) -> "CommandInfo":
        return CommandInfo(
            name=cmd.name,
            pattern=cmd.pattern._origin,
            declaration=_get_function_declaration(cmd._runner),
            docstring=inspect.getdoc(cmd._runner) or "",
        )


class TypeInfo(BaseModel):
    name: str
    pattern: str
    fields: str  # "field_name: TypeName, ..." summary of annotated class attributes
    docstring: str

    def as_text(self) -> str:
        return " | ".join(v for v in self.model_dump().values() if v)

    @staticmethod
    def from_type(object_type: ObjectType) -> "TypeInfo":
        fields_parts = []
        for attr_name, annotation in inspect.get_annotations(object_type).items():
            type_name = annotation.__name__ if hasattr(annotation, "__name__") else str(annotation)
            fields_parts.append(f"{attr_name}: {type_name}")
        return TypeInfo(
            name=object_type.__name__,
            pattern=object_type.pattern._origin,
            fields=", ".join(fields_parts),
            docstring=inspect.getdoc(object_type) or "",
        )


def _get_function_declaration(func) -> str:
    get_name = lambda x: x.__name__ if hasattr(x, "__name__") else x

    signature = inspect.signature(func)
    parameters = []

    for name, parameter in signature.parameters.items():
        param_str = name

        if parameter.annotation != inspect.Parameter.empty:
            param_str += f": {get_name(parameter.annotation)}"

        if parameter.default != inspect.Parameter.empty:
            default_value = parameter.default
            if default_value is None:
                default_str = "None"
            elif isinstance(default_value, str):
                default_str = f"'{default_value}'"
            else:
                default_str = str(default_value)
            param_str += f" = {default_str}"

        parameters.append(param_str)

    func_type = "async def" if inspect.iscoroutinefunction(func) else "def"
    parameters_str = ", ".join(parameters)
    return_annotation = get_name(signature.return_annotation)

    if signature.return_annotation != inspect.Parameter.empty:
        return f"{func_type} {func.__name__}({parameters_str}) -> {return_annotation}"
    else:
        return f"{func_type} {func.__name__}({parameters_str})"


class StarkJsonEncoder(json.JSONEncoder):
    def default(self, o):
        obj = o
        if hasattr(obj, "__json__"):
            return obj.__json__()

        elif isinstance(obj, Pattern):
            return {"origin": obj._origin}

        elif isinstance(obj, Command):
            return CommandInfo.from_command(obj).model_dump()

        elif isinstance(obj, CommandsManager):
            return {
                "name": obj.name,
                "commands": obj.commands,
            }

        else:
            return super().default(obj)
