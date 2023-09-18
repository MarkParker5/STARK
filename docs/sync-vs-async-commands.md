# Sync vs Async Commands

## TLDR

- **Needs await**: If you're using third-party libraries that require `await`, such as:
```py
results = await some_library()
```
Declare your command using `async def`:
```py
@manager.new('hello')
async def hello_command() -> Response:
    text = voice = await some_library()  # asynchronous call
    return Response(text=text, voice=voice)
```

- **Blocking Code**: If your command contains blocking synchronous code (e.g., using the `requests` library or `time.sleep`), declare it using `def`:
```py
import requests

@manager.new('hello')
def hello_command() -> Response:
    requests.get('https://stark.markparker.me/')  # synchronous blocking code
    text = voice = 'Hello, world!'
    return Response(text=text, voice=voice)
```

- **Only Fast Code**: For commands that don't need to wait for external responses or perform computations, you can use `async def`.

- **Unsure?**: If you just don't know, use normal `def`.

- **Mix of Blocking and Async**: If your command contains both blocking code and `await`-requiring asynchronous code, you'll need to use [asyncer](https://asyncer.tiangolo.com). There are two methods:

 1. **Recommended**: Declare the command with `async def`, use `await` for asynchronous functions, and wrap blocking code in `asyncer.asyncify`:
 ```py
    import asyncer
    import requests

    @manager.new('hello')
    async def hello_command() -> Response:
        await some_library()  # asynchronous function
        await asyncer.asyncify(requests.get)('https://stark.markparker.me/')  # converted to asynchronous
        text = voice = 'Hello, world!'
        return Response(text=text, voice=voice)
```

  2. Use a regular `def` for the command, execute blocking functions as-is, and wrap asynchronous functions in `asyncer.syncify`:
```py
    import asyncer
    import requests

    @manager.new('hello')
    def hello_command() -> Response:
        asyncer.syncify(some_library)()  # converted to synchronous
        requests.get('https://stark.markparker.me/')  # blocking code
        text = voice = 'Hello, world!'
        return Response(text=text, voice=voice)
```

## Technical Details

All commands in Stark are inherently asynchronous. If you declare a command as synchronous, Stark converts it to asynchronous using [asyncer.asyncify](https://asyncer.tiangolo.com/).

By default, Stark concurrently manages two vital processes: speech transcription and response handling. It also has to execute commands, adding temporary processes that last as long as the command. All these processes share a single main thread. If one process blocks the thread for an extended period (e.g., with `requests.get` or `time.sleep`), it can halt the entire application. Stark includes the `BlockageDetector` to monitor the main thread and alert you if it's blocked for longer than a specified duration (default is 1 second). Additionally, every command is timed to help identify any that might be causing blockages.

For commands that might cause blockages, declaring them using def is advised. Stark will then wrap these commands with asyncer.asyncify, spawning separate background threads for each process

When using async def, care should be taken to prevent the main thread from being blocked. This can be achieved by avoiding long-blocking code and opting for asynchronous libraries like `aiohttp` over synchronous ones such as `requests`. Additionally, `asyncer.asyncify` can be used to wrap blocking sections of code.

For a deeper dive into synchronous vs. asynchronous programming, check [FastAPI documentation](https://fastapi.tiangolo.com/async/). To learn more about transitioning between functions and threads, refer to the [asyncer documentation](https://asyncer.tiangolo.com/).
