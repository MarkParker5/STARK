from typing import Callable


class classproperty[GetterReturnType]:
    def __init__(self, func: Callable[..., GetterReturnType]):
        if isinstance(func, (classmethod, staticmethod)):
            fget = func
        else:
            fget = classmethod(func)
        self.fget = fget

    def __get__(self, obj, klass=None) -> GetterReturnType:
        if klass is None:
            klass = type(obj)
        return self.fget.__get__(obj, klass)()

# from typing import Any, Callable

# def classproperty[T](fget: Callable[[type[Any]], T]) -> T:
#     class _ClassProperty(property):
#         def __get__(self, cls: type[Any], owner: type[Any]) -> T: # type: ignore
#             return classmethod(fget).__get__(None, owner)()
#     return _ClassProperty(fget) # type: ignore
