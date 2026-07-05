# Sync vs Async Commands

## TLDR

### Needs await

If you're using third-party libraries that require `await`, such as

```py
results = await some_library()
```

Declare your command using `async def`:

```py
@manager.new('hello')
async def hello_command() -> Response:
    return Response(await some_library())  # asynchronous call
```

### Blocking Code

If your command contains blocking synchronous code (e.g., using the `requests` library or `time.sleep`), declare it using `def`:

```py
import requests

@manager.new('hello')
def hello_command() -> Response:
    requests.get('https://stark.markparker.me/')  # synchronous blocking code
    return Response('Hello, Stark!')
```

### Only Fast Code

For commands that don't need to wait for external responses or perform long computations, you can use both `async def` and `def`.

### Unsure?

If you just don't know, use normal `def`.

### Mix of Blocking and Async

If your command contains both blocking code and `await`-requiring asynchronous code, you'll need to use [asyncer](https://asyncer.tiangolo.com). There are two methods:

1. **Recommended**: Declare the command with `async def`, use `await` for asynchronous functions, and wrap blocking code in `asyncer.asyncify`:

```py
import asyncer
import requests

@manager.new('hello')
async def hello_command() -> Response:
    await some_library() # asynchronous function
    await asyncer.asyncify(requests.get)('https://stark.markparker.me/') # converted to asynchronous
    return Response('Hello, Stark!')
```

2. Use a regular `def` for the command, execute blocking functions as-is, and wrap asynchronous functions in `asyncer.syncify`:

```py
import asyncer
import requests

@manager.new('hello')
def hello_command() -> Response:
    asyncer.syncify(some_library)() # converted to synchronous
    requests.get('https://stark.markparker.me/') # blocking code
    return Response('Hello, Stark!')
```

## Technical Details

All commands in Stark are inherently asynchronous. If you declare a command as synchronous, Stark converts it to asynchronous using [asyncer.asyncify](https://asyncer.tiangolo.com/).

By default, Stark concurrently manages two vital processes: speech transcription and response handling. It also has to execute commands, adding temporary processes that last as long as the command. All these processes share a single main thread. If one process blocks the thread for an extended period (e.g., with `requests.get` or `time.sleep`), it can halt the entire application. Stark includes the `BlockageDetector` to monitor the main thread and alert you if it's blocked for longer than a specified duration (default is 1 second).

For commands that might cause blockages, declaring them using def is advised. Stark will then wrap these commands with asyncer.asyncify, spawning separate background threads for each process.

When using async def, care should be taken to prevent the main thread from being blocked. This can be achieved by avoiding long-blocking code and opting for asynchronous libraries like `aiohttp` over synchronous ones such as `requests`. Additionally, `asyncer.asyncify` can be used to wrap blocking sections of code.

For a deeper dive into synchronous vs. asynchronous programming, check [FastAPI documentation page](https://fastapi.tiangolo.com/async/). To learn more about transitioning between functions and threads, refer to the [asyncer documentation](https://asyncer.tiangolo.com/).

## Background Commands

Async commands aren't just for non-blocking I/O, they're how STARK powers "fire it and keep going" commands: start a task, respond immediately, keep running in the background, and push progress updates as they happen. The assistant stays free to handle other input the whole time; it isn't blocked waiting on the command to finish.

```py
import anyio
from stark.core import AsyncResponseHandler

timer_cancelled = False

@manager.new('start timer')
async def start_timer(handler: AsyncResponseHandler) -> Response:
    global timer_cancelled
    timer_cancelled = False
    await handler.respond(Response('Timer started.', commands=[stop_timer]))  # 1
    for percent in (25, 50, 75, 100):
        await anyio.sleep(15)                                                       # 2
        if timer_cancelled:
            return Response('Timer stopped.')                                  # 3
        await handler.respond(Response(f'Timer {percent}% done.'))
    return Response('Timer finished!')

@manager.new('stop timer', hidden=True)
async def stop_timer(handler: AsyncResponseHandler) -> Response:
    global timer_cancelled
    timer_cancelled = True
    handler.pop_context()
    return Response('Stopping timer...')
```

1. The command responds immediately and offers a `stop timer` command, scoped to this context only, see [Commands Context](https://stark.markparker.me/commands-context/index.md) for how `commands=[...]` scoping works.
1. It keeps running, four checkpoints, 15 seconds apart, pushing a `Response` every time there's something new to report. Each `respond` call is queued and delivered without blocking the rest of the assistant, see [Command Response](https://stark.markparker.me/command-response/index.md).
1. A plain global flag is enough to cancel it, checked once per checkpoint. `stop timer` is only reachable while the timer is running (it's offered via `commands=[stop_timer]` above, not registered at the root). If you need command-local state instead of a shared global, define `stop_timer` inside `start_timer` so it closes over the same variables.

Why doesn't the assistant just sit there waiting for the timer to finish? Because it's never blocked in the first place, the loop above runs as one of several concurrent tasks `CommandsContext` manages, and `handle_responses` delivers each response as it's queued, regardless of what else is in flight. What the user experiences while a background command runs, does the assistant repeat progress, stay silent until summoned, or wait for a "stop" word, is governed by [Voice Assistant & Modes](https://stark.markparker.me/voice-assistant/index.md), not by the command itself.

This same pattern, immediate response, periodic progress, optional cancel, is what would back a download tracker, a long-running search, or any task that shouldn't make the user wait in silence.
