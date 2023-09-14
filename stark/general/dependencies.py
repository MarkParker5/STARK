from typing import Callable, Any
from dataclasses import dataclass


@dataclass
class Dependency:
    name: str | None
    annotation: type
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
    
    def resolve(self, callable: Callable) -> dict[str, Any]:
        parameters = {}
        for name, annotation in callable.__annotations__.items():
            for dependency in self.dependencies:
                if dependency.annotation == annotation and (dependency.name == name or not dependency.name):
                    parameters[name] = dependency.value
        return parameters
        
    def add_dependency(self, name: str | None, annotation: type, value: Any):
        self.dependencies.add(Dependency(name, annotation, value))
                
default_dependency_manager = DependencyManager()
default_dependency_manager.add_dependency(None, DependencyManager, default_dependency_manager)
