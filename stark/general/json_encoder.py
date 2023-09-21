# from typing import _SpecialGenericAlias
import json
import inspect
from stark import Pattern, Command, CommandsManager


class StarkJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, '__json__'):
            return obj.__json__()
        
        elif isinstance(obj, Pattern):
            return {
                'origin': obj._origin
            }
            
        elif isinstance(obj, Command):
            return {
                'name': obj.name,
                'pattern': obj.pattern,
                'declaration': self.get_function_declaration(obj._runner),
                'docstring': inspect.getdoc(obj._runner) or ''
            }
            
        elif isinstance(obj, CommandsManager):
            return {
                'name': obj.name,
                'commands': obj.commands,
            }
            
        else:
            return super().default(obj)
        
    def get_function_declaration(self, func):
        get_name = lambda x: x.__name__ if hasattr(x, '__name__') else x
        
        # return inspect.getsourcelines(func)[0][:2]
        
        signature = inspect.signature(func)
        parameters = []
        
        for name, parameter in signature.parameters.items():
            
            # if issubclass(parameter.annotation, _SpecialGenericAlias): for typing.Generator and etc
            #     parameters.append(str(parameter))
            #     continue
            
            param_str = name
            
            if parameter.annotation != inspect.Parameter.empty:
                annotation = get_name(parameter.annotation)
                param_str += f': {annotation}'
            
            if parameter.default != inspect.Parameter.empty:
                default_value = parameter.default
                
                if default_value is None:
                    default_str = 'None'
                elif isinstance(default_value, str):
                    default_str = f"'{default_value}'"
                else:
                    default_str = str(default_value)
                
                param_str += f' = {default_str}'
            
            parameters.append(param_str)
            
        func_type = 'async def' if inspect.iscoroutinefunction(func) else 'def'
        name = func.__name__
        parameters_str = ', '.join(parameters)
        return_annotation = get_name(signature.return_annotation)
        
        if signature.return_annotation != inspect.Parameter.empty:
            return f'{func_type} {name}({parameters_str}) -> {return_annotation}'
        else:
            return f'{func_type} {name}({parameters_str})'

