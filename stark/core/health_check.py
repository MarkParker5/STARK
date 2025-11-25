import warnings

from stark.core.command import Command
from stark.core.parsing import PatternParser


def health_check(pattern_parser: PatternParser, commands: list[Command]) -> None:
    # TODO: update schema and validation; handle optional parameters; handle short form where type is defined in object

    # 1. Registered types: pattern parameters and annotations match; all used types are registered
    for reg_type in pattern_parser.parameter_types_by_name.values():
        pattern_params = set(reg_type.type.pattern.parameters.keys())
        class_params = set(reg_type.type.__annotations__.keys())
        assert pattern_params <= class_params, (
            f"Pattern parameters {pattern_params} do not match class annotations {class_params} for {reg_type.type.__name__}"
        )
        # 2. Registered types: All referenced parameter types are registered
        for param_name in pattern_params:
            assert reg_type.type.pattern.parameters[param_name].type_name in pattern_parser.parameter_types_by_name, (
                f"Unknown parameter type '{param_name}' in pattern '{reg_type.type.pattern}' of type '{reg_type.type.__name__}'. Known types: {sorted(pattern_parser.parameter_types_by_name.keys())}"
            )

    # 3. No duplicate parameter types registered
    type_names = list(pattern_parser.parameter_types_by_name.keys())
    if len(type_names) != len(set(type_names)):
        duplicates = {name for name in type_names if type_names.count(name) > 1}
        assert not duplicates, f"Duplicate parameter type names found: {sorted(duplicates)}"

    # 4. Commands: All referenced parameter types are registered
    for command in commands:
        for param in command.pattern.parameters.values():
            assert param.type_name in pattern_parser.parameter_types_by_name, (
                f"Unknown parameter type '{param.type_name}' in pattern '{command.pattern}' of command '{command.name}'. Known types: {sorted(pattern_parser.parameter_types_by_name.keys())}"
            )

    # 5. Commands: all pattern params are expected by the runner func
    for command in commands:
        pattern_params = set(command.pattern.parameters.keys())
        runner_params = set(command._runner.__annotations__.keys())
        assert pattern_params <= runner_params, f"Command '{command.name}' function missing parameters: {pattern_params - runner_params}"

    # 6. Pattern syntax validity (TODO)
    # for command in commands:
    #     assert command.pattern.is_valid(), f"Invalid pattern syntax: {command.pattern.origin}"

    # 7. No unused types
    used_types = {param.type_name for command in commands for param in command.pattern.parameters.values()}
    for type_name in pattern_parser.parameter_types_by_name:
        # assert type_name in used_types, f"Registered type {type_name} is not used in any pattern"
        if type_name not in used_types:
            warnings.warn(f"Registered type {type_name} is not used in any pattern")
