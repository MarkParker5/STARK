from typing import Callable, Any
from dataclasses import dataclass


@dataclass
class Dependency:
    name: str | None
    annotation: type | None
    value: Any
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Dependency):
            raise TypeError(f"Cannot compare Dependency with {type(other)}")
        return self.name == other.name and self.annotation == other.annotation
    
    def __hash__(self):
        return hash((self.name, self.annotation))

class DependencyManager:
    
    dependencies: set[Dependency]
    
    def __init__(self):
        self.dependencies = set()
        
    def find(self, name: str | None, annotation: type | None) -> Dependency | None:
        for dependency in self.dependencies:
            name_match = name == dependency.name
            annotation_match = annotation == dependency.annotation
            if (not dependency.name or name_match) and annotation_match:
                return dependency
        return None
    
    def resolve(self, func: Callable) -> dict[str, Any]:
        parameters = {}
        
        annotations = {name: None for name in func.__code__.co_varnames}
        annotations.update(func.__annotations__)
        
        for name, annotation in annotations.items():
            if dependency := self.find(name, annotation):
                parameters[name] = dependency.value

        return parameters
        
    def add_dependency(self, name: str | None, annotation: type | None, value: Any):
        assert (name or annotation) and value
        self.dependencies.add(Dependency(name, annotation, value))
                
default_dependency_manager = DependencyManager()
default_dependency_manager.add_dependency(None, DependencyManager, default_dependency_manager)
