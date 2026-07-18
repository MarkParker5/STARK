import warnings

from stark.core.command import Command
from stark.core.parsing import _LOCALIZER_KEY_REGEX, PatternParser


def health_check(pattern_parser: PatternParser, commands: list[Command]) -> None:
    # TODO: update schema and validation; handle optional parameters; handle short form where type is defined in object

    # 1. Registered types: pattern parameters and annotations match; all used types are registered
    for reg_type in pattern_parser.parameter_types_by_name.values():
        for lang, type_pattern in reg_type.type.patterns.items():
            pattern_params = set(type_pattern.parameters.keys())
            class_params = set(reg_type.type.__annotations__.keys())
            assert pattern_params <= class_params, (
                f"Pattern parameters {pattern_params} do not match class annotations {class_params} for {reg_type.type.__name__} (language '{lang}')"
            )
            # 2. Registered types: All referenced parameter types are registered
            for param_name in pattern_params:
                assert type_pattern.parameters[param_name].type_name in pattern_parser.parameter_types_by_name, (
                    f"Unknown parameter type '{param_name}' in pattern '{type_pattern}' of type '{reg_type.type.__name__}' (language '{lang}'). Known types: {sorted(pattern_parser.parameter_types_by_name.keys())}"
                )

    # 3. No duplicate parameter types registered
    type_names = list(pattern_parser.parameter_types_by_name.keys())
    if len(type_names) != len(set(type_names)):
        duplicates = {name for name in type_names if type_names.count(name) > 1}
        assert not duplicates, f"Duplicate parameter type names found: {sorted(duplicates)}"

    # 4. Commands: validate @key references and parameter types
    for command in commands:
        for lang, cmd_pattern in command.patterns.items():
            if pattern_parser.localizer and pattern_parser._has_localizer_keys(cmd_pattern):
                for key in _LOCALIZER_KEY_REGEX.findall(cmd_pattern._origin):
                    pattern_parser.localizer.verify_recognizable(key)
        for param in command.get_pattern("base").parameters.values():
            assert param.type_name in pattern_parser.parameter_types_by_name, (
                f"Unknown parameter type '{param.type_name}' in pattern '{command.get_pattern('base')}' of command '{command.name}'. Known types: {sorted(pattern_parser.parameter_types_by_name.keys())}"
            )

    # 5. Commands: all pattern params are expected by the runner func
    for command in commands:
        pattern_params = set(command.get_pattern("base").parameters.keys())
        runner_params = set(command._runner.__annotations__.keys())
        assert pattern_params <= runner_params, (
            f"Command '{command.name}' function missing parameters: {pattern_params - runner_params}"
        )

    # 6. Pattern syntax validity (TODO)
    # for command in commands:
    #     assert command.get_pattern("base").is_valid(), f"Invalid pattern syntax: {command.get_pattern("base").origin}"

    # 7. Try compiling all patterns to catch syntax errors early
    for reg_type in pattern_parser.parameter_types_by_name.values():
        for lang, p in reg_type.type.patterns.items():
            try:
                pattern_parser._compile_pattern(p, language_code=lang)
            except Exception as e:
                warnings.warn(
                    f"Failed to compile pattern '{p}' of type '{reg_type.type.__name__}' (language '{lang}'): {e}"
                )
    for command in commands:
        for lang, p in command.patterns.items():
            try:
                pattern_parser._compile_pattern(p, language_code=lang)
            except Exception as e:
                warnings.warn(f"Failed to compile pattern '{p}' of command '{command.name}' (language '{lang}'): {e}")

    # 8. No unused types
    used_types = {param.type_name for command in commands for param in command.get_pattern("base").parameters.values()}
    for type_name in pattern_parser.parameter_types_by_name:
        # assert type_name in used_types, f"Registered type {type_name} is not used in any pattern"
        if type_name not in used_types:
            warnings.warn(f"Registered type {type_name} is not used in any pattern")
