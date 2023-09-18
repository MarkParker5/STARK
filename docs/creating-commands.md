# Creating Commands

Commands serve as foundational building blocks designed to execute specific actions. They can be implemented either synchronously or asynchronously. In the following sections, we'll explore the specific features of each type and their differences.

---

## Sync Commands

### **Simple Command with return (sync)**

A synchronous command can straightforwardly return a response, as demonstrated below:

```python
from stark import Response, CommandsManager

manager = CommandsManager()

@manager.new('hello')
def hello_command() -> Response:
    text = voice = 'Hello, world!'
    return Response(text=text, voice=voice)
```

### **Multiple responses using yield (sync)**

Although it's possible to yield multiple responses in synchronous functions, doing so may block the main thread. This can result in warnings or even halt the application. For multiple responses in sync functions, consider using the `ResponseHandler.respond` method or contemplate migrating to the [async](/sync-vs-async-commands) option.

```python
@manager.new('foo')
def foo() -> Response:
    yield Response(text='Hello')
    yield Response(text='World')
    # more yields...
```

### **Multiple responses using ResponseHandler.respond (sync)**

To manage multiple responses, the `ResponseHandler` can be leveraged. Simply include a property of type `ResponseHandler`, and the [dependency injection](/dependency-injection) mechanism will handle it automatically.

```python
@manager.new('foo')
def foo(handler: ResponseHandler):
    handler.respond(Response(text='Starting task'))
    # some processing
    handler.respond(Response(text='Task progress is 50%'))
    ...
    handler.respond(Response(text='Task is done'))
```

### **Remove response using ResponseHandler.unrespond (sync)**

To remove a response, use the `unrespond` method. If the voice assistant is in waiting mode, the response won't be repeated in the subsequent interaction. Learn more about modes in [Voice Assistant](/voice-assistant.md).

```python
@manager.new('foo')
def foo(handler: ResponseHandler):
    handler.respond(Response(text='Starting task'))
    ...
    error = Response(text='No internet connection, retrying task...')
    handler.respond(error)
    ...
    # when the internet connection is restored
    handler.unrespond(error)
    handler.respond(Response(text='Task is done'))
```

### **Call command from another command (sync)**

Commands are inherently async, so we need to syncify the async foo (or declare the current function as async and await foo, see [Sync vs Async](/sync-vs-async-commands))

* **Simple:**

```python
from asyncer import syncify
...

@manager.new('foo')
def foo() -> Response:
    return Response(text='Hello!')

@manager.new('bar')
def bar() -> Response: 
    sync_foo = syncify(foo)
    return sync_foo()
```

* **With dependency injection:**

Include the `inject_dependencies` property in the function declaration. This function wraps the command for smooth dependency injection. Learn more about dependencies at [DI Container](/dependency-injection).

```python
@manager.new('bar')
def bar(inject_dependencies): 
    return syncify(inject_dependencies(foo))()
```

---

## Async Commands

Asynchronous commands resemble their synchronous counterparts but offer enhanced features like `await` and `yield`.

### **Simple Command with return (async)**

An asynchronous command can effortlessly return a response:

```python
@manager.new('hello')
async def hello_command() -> Response:
    text = voice = 'Hello, world!'
    return Response(text=text, voice=voice)
```

### **Multiple responses using yield (async)**

Yielding multiple responses in asynchronous functions is seamless and doesn't block the main thread.

```python
@manager.new('foo')
async def foo() -> Response:
    yield Response(text='Starting task')
    # some processing
    yield Response(text='Task progress is 50%')
    ...
    yield Response(text='Task is done')
```

### **Multiple responses using ResponseHandler.respond (async)**

As an alternative to `yield`, the asynchronous version of `ResponseHandler`, named `AsyncResponseHandler`, can be used.

```python
@manager.new('foo')
async def foo(handler: AsyncResponseHandler):
    await handler.respond(Response(text='Starting task'))
    # some processing
    await handler.respond(Response(text='Task progress is 50%'))
    ...
    await handler.respond(Response(text='Task is done'))
```

### **Remove response using ResponseHandler.unrespond (async)**

To remove a response, use the `unrespond` method. If the voice assistant is in waiting mode, the response won't be repeated in the subsequent interaction. Learn more about modes in [Voice Assistant](/voice-assistant.md).

```python
@manager.new('foo')
async def foo(handler: AsyncResponseHandler):
    await handler.respond(Response(text='Starting task'))
    ...
    error = Response(text='No internet connection, retrying task...')
    await handler.respond(error)
    ...
    # once the internet connection is restored
    await handler.unrespond(error)
    await handler.respond(Response(text='Task is done'))
```

Do note that you can delete responses sent using `yield` in the same manner. There's no distinction between the two.

### **Call command from another command (async)**

Commands can be invoked as if they were standard functions.

* **Simple:**

```python
@manager.new('foo')
async def foo() -> Response:
    return Response(text='Hello!')

@manager.new('bar')
async def bar():
    return await foo()
```

* **With dependency injection:**

For commands with dependencies, the `inject_dependencies` wrapper ensures seamless injection.

```python
@manager.new('foo')
async def foo(handler: AsyncResponseHandler) -> Response:
    handler.respond(Response(text='Hello!'))

@manager.new('bar')
async def bar(inject_dependencies): 
    return await inject_dependencies(foo)()
```

---

## **Extending/merging commands managers**

Command managers can be expanded by merging child managers into them.

```python
root_manager = CommandsManager()
child_manager = CommandsManager('Child')

@root_manager.new('test')
def test(): pass

@child_manager.new('test2')
def test2(): pass

root_manager.extend(child_manager) # now root_manager has all commands of child_manager
```

---

In conclusion, the foundational concepts remain consistent whether you employ synchronous or asynchronous commands. The primary distinction is in task handling: asynchronous commands facilitate non-blocking execution. As always, opt for the approach that best aligns with your application's specific requirements.
