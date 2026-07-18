# Creating Commands

Commands serve as foundational building blocks designed to execute specific actions. They can be implemented either synchronously or asynchronously. In the following sections, we'll explore the specific features of each type and their differences. <small>([jump to async commands →](#async-commands), full comparison in [Sync vs Async Commands](sync-vs-async-commands.md))</small>

---

## Sync Commands

### Simple Command with `return` 

A synchronous command can straightforwardly return a response, as demonstrated below:

```python
from stark import Response, CommandsManager

manager = CommandsManager()

@manager.new('hello')
def hello_command() -> Response:
    return Response('Hello, Stark!')
```

### Multiple responses using `yield` 

Although it's possible to yield multiple responses in synchronous functions, doing so may block the main thread. This can result in warnings or even halt the application. For multiple responses in sync functions, consider using the `ResponseHandler.respond` method or contemplate migrating to the [async](sync-vs-async-commands.md) option.

```python
@manager.new('start timer')
def start_timer() -> Response:
    yield Response('Timer started')
    yield Response('Timer finished')
    # more yields...
```

### Multiple responses using `ResponseHandler.respond` 

To manage multiple responses, the `ResponseHandler` can be leveraged. Simply include a property of type `ResponseHandler`, and the [dependency injection](dependency-injection.md) mechanism will handle it automatically.

```python
@manager.new('start timer')
def start_timer(handler: ResponseHandler):
    handler.respond(Response('Timer started'))
    # some processing
    handler.respond(Response('Timer 50% done'))
    ...
    handler.respond(Response('Timer finished'))
```

### Remove response using `ResponseHandler.unrespond` 

To remove a response, use the `unrespond` method. If the voice assistant is in waiting mode, the response won't be repeated in the subsequent interaction. Learn more about modes in [Voice Assistant](voice-assistant.md).

```python
@manager.new('download update')
def download_update(handler: ResponseHandler):
    handler.respond(Response('Downloading...'))
    ...
    error = Response('No internet connection, retrying...')
    handler.respond(error)
    ...
    # when the internet connection is restored
    handler.unrespond(error)
    handler.respond(Response('Download complete'))
```

### Call command from another command 

Commands are inherently async, so we need to syncify the async `lights_off` (or declare the current function as `async def` and await it directly, see [Async Commands](#async-commands) below).

#### Simple

```python
from asyncer import syncify
...

@manager.new('turn off the light')
def lights_off() -> Response:
    return Response('Lights off.')

@manager.new('good night')
def good_night() -> Response: 
    sync_lights_off = syncify(lights_off)
    return sync_lights_off()
```

#### With dependency injection

Include the `inject_dependencies` property in the function declaration. This function wraps the command for smooth dependency injection. Learn more about dependencies at [DI Container](dependency-injection.md).

You need this over the simple version above whenever the called command itself takes injected dependencies (a `ResponseHandler`, the language code, a custom dependency), calling it directly would skip injection and the parameter would never get filled in. `inject_dependencies` resolves those first, then calls the command.

```python
@manager.new('good night')
def good_night(inject_dependencies): 
    return syncify(inject_dependencies(lights_off))()
```

---

## Async Commands

Asynchronous commands resemble their synchronous counterparts but offer enhanced features like `await` and `yield`.

### Simple Command with `return` 

An asynchronous command can effortlessly return a response:

```python
@manager.new('hello')
async def hello_command() -> Response:
    return Response('Hello, Stark!')
```

### Multiple responses using `yield` 

Yielding multiple responses in asynchronous functions is seamless and doesn't block the main thread.

```python
@manager.new('start timer')
async def start_timer() -> Response:
    yield Response('Timer started')
    # some processing
    yield Response('Timer 50% done')
    ...
    yield Response('Timer finished')
```

### Multiple responses using `ResponseHandler.respond` 

As an alternative to `yield`, the asynchronous version of `ResponseHandler`, named `AsyncResponseHandler`, can be used.

```python
@manager.new('start timer')
async def start_timer(handler: AsyncResponseHandler):
    await handler.respond(Response('Timer started'))
    # some processing
    await handler.respond(Response('Timer 50% done'))
    ...
    await handler.respond(Response('Timer finished'))
```

### Remove response using `ResponseHandler.unrespond` 

To remove a response, use the `unrespond` method. If the voice assistant is in waiting mode, the response won't be repeated in the subsequent interaction. Learn more about modes in [Voice Assistant](voice-assistant.md).

```python
@manager.new('download update')
async def download_update(handler: AsyncResponseHandler):
    await handler.respond(Response('Downloading...'))
    ...
    error = Response('No internet connection, retrying...')
    await handler.respond(error)
    ...
    # once the internet connection is restored
    await handler.unrespond(error)
    await handler.respond(Response('Download complete'))
```

Do note that you can delete responses sent using `yield` in the same manner. There's no distinction between the two.

### Call command from another command 

Commands can be invoked as if they were standard async functions (coroutines).

#### Simple

```python
@manager.new('turn off the light')
async def lights_off() -> Response:
    return Response('Lights off.')

@manager.new('good night')
async def good_night():
    return await lights_off()
```

#### With dependency injection

For commands with dependencies, the `inject_dependencies` wrapper ensures seamless injection.

```python
@manager.new('turn off the light')
async def lights_off(handler: AsyncResponseHandler) -> Response:
    handler.respond(Response('Lights off.'))

@manager.new('good night')
async def good_night(inject_dependencies): 
    return await inject_dependencies(lights_off)()
```

---

## Extending/merging commands managers

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

What happens when nothing matches? Register a wildcard command as a catch-all, see [Fallback Command / LLM Integration](advanced/fallback-command-llm-integration.md).

This page covered the mechanics of writing a command. For everything a `Response` can carry and how patterns extract parameters, see [Core Concepts](core-concepts.md).
