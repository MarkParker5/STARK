# from typing import Callable


# works with pyright/mypy, doesn't work with pydantic
# class classproperty[GetterReturnType]:
#     def __init__(self, func: Callable[..., GetterReturnType]):
#         if isinstance(func, (classmethod, staticmethod)):
#             fget = func
#         else:
#             fget = classmethod(func)
#         self.fget = fget

#     def __get__(self, obj, klass=None) -> GetterReturnType:
#         if klass is None:
#             klass = type(obj)
#         return self.fget.__get__(obj, klass)()


# works with pydantic, doesn't pass pyright/mypy

def classproperty[T](fget):
    class _ClassProperty(property):
        def __get__(self, cls, owner): # type: ignore
            return classmethod(fget).__get__(None, owner)()
    return _ClassProperty(fget)
