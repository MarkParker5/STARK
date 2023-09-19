# Dependency Injection

Dependency Injection (DI) is a powerful design pattern used to achieve Inversion of Control (IoC) between classes and their dependencies. Within the context of our voice assistant, Dependency Injection facilitates the provision of specific objects or values to command functions. This ensures that these functions can readily access external resources or other system components.

This guide provides an overview of the Dependency Injection implementation, how to utilize it in your voice assistant, and some native dependencies.

## Response Handler

There are two response handlers: `AsyncResponseHandler` and `ResponseHandler`. They oversee the processing of responses, asynchronously and synchronously, respectively. To employ them, simply include the required type (class) annotation as an argument within the function declaration. The argument's name isn't significant for this dependency.

```python
@manager.new('hello')
async def hello(handler: AsyncResponseHandler) -> Response: 
    await handler.respond(Response(text = 'Hi'))
```

In the showcased example, the `AsyncResponseHandler` is automatically injected into the `foo` command function upon its invocation.

## `inject_dependency`

The `inject_dependency` method serves to integrate specific dependencies into a function. This method determines the function's dependencies and subsequently calls it. Contrary to the response handler, this dependency is identified by the argument's name.

Example:
```python
@manager.new('foo')
async def foo(handler: AsyncResponseHandler) -> Response: 
    return Response(text = 'foo!')

@manager.new('bar')
async def bar(inject_dependencies): 
    return await inject_dependencies(foo)()
```

Here, the `foo` dependency is injected and executed within the `bar` command function.

## Accessing DIContainer in a Command

The `CommandsContext` class initializes with a `dependency_manager` of the `DependencyManager` type. This manager undertakes the role of identifying and injecting the requisite dependencies for command functions.

To tap into the DIContainer inside a command, simply declare the needed dependency as a command function parameter. The `DependencyManager` will resolve this parameter and supply the appropriate object or value.

For more advanced access, you can extract the container as a dependency of type `DIContainer`, as demonstrated:

```python
@manager.new('baz')
async def baz(di_container: DIContainer): 
    di_container.add_dependency(...)
    di_container.find(...)
```

This is feasible because the default DI container internally registers itself as a dependency:

```python
default_dependency_manager.add_dependency(None, DependencyManager, default_dependency_manager)
```

## Adding Custom Dependency

You can incorporate custom dependencies using the `add_dependency` method of the default shared instance of `DependencyManager`.

Example:
```python
from stark.general.dependencies import default_dependency_manager
...
default_dependency_manager.add_dependency("custom_name", CustomType, custom_value)
```

In this instance, a new dependency named `custom_name`, of `CustomType`, with the value `custom_value` is appended. If the name is set to `None`, you can later choose any name for the function argument; the dependency will be discerned solely by type (like `ResponseHandler` and `AsyncResponseHandler`). Conversely, setting the type to `None` allows the dependency to be detected purely by the argument name (like `inject_dependencies`).

## Creating a Custom Container

To employ a custom container for Dependency Injection in lieu of the default one, instantiate a new `DependencyManager` and input your custom dependencies. This tailored container can subsequently be utilized during the `CommandsContext` initialization.

Example:
```python
custom_dependency_manager = DependencyManager()
custom_dependency_manager.add_dependency(...)

context = CommandsContext(..., dependency_manager=custom_dependency_manager)
```

It's worth noting that the CommandsContext always registers several native dependencies upon initialization:

```python
self.dependency_manager.add_dependency(None, AsyncResponseHandler, self)
self.dependency_manager.add_dependency(None, ResponseHandler, SyncResponseHandler(self))
self.dependency_manager.add_dependency('inject_dependencies', None, self.inject_dependencies)
```

However, other native dependencies will be absent in the custom container unless you manually incorporate them.

---

The adaptability provided by the Dependency Injection framework ensures your command functions remain modular, simplifying testing. As you further develop your voice assistant, utilize this system to adeptly handle your dependencies.
