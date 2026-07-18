# Optimization for Stark

A S.T.A.R.K. assistant runs almost everything, speech transcription, response delivery, and every executing command, on one main thread via [anyio](https://anyio.readthedocs.io/) task groups (see [Custom Run](custom-run.md) for exactly which tasks). That's what makes it fast and lightweight by default, but it means a single blocking call can stall the entire assistant, not just the command that made it. This page is about avoiding that, and a few other places performance tends to matter.

## Non-blocking is Key

**THE MOST IMPORTANT**: Always ensure that you **DO NOT** place blocking code inside `async def` functions. Blocking code can drastically reduce the performance of asynchronous applications by halting the execution of other parts of the application.

If you have commands that run blocking code, always define them using the simple `def` ([Sync-vs-Async](../sync-vs-async-commands.md)). This ensures that Stark creates a separate worker thread to handle the execution of that command. By doing so, Stark remains responsive, even when processing resource-intensive commands.

## Sync vs Async

Understanding the difference between synchronous and asynchronous code is crucial. Asynchronous code allows your application to perform other tasks while waiting for a particular task to complete, thus improving efficiency. The [Sync-vs-Async](../sync-vs-async-commands.md) page provides a comprehensive comparison and guidance on how to effectively leverage both.

## Utilizing the asyncer

The [asyncer](https://asyncer.tiangolo.com) documentation is a valuable resource. It provides an array of tools and methods to help convert synchronous code to asynchronous and vice-versa, aiding in the optimization process.

## Using asyncer.asyncify

If you need to call blocking synchronous code within an `async def` function, utilize `asyncer.asyncify`. It allows you to effectively run synchronous code inside an asynchronous function without blocking the entire event loop.

## Grouping Asynchronous Requests

If you have multiple asynchronous tasks that can be executed concurrently, group them together and await them as one unit. This approach allows tasks to be run simultaneously, improving the overall speed of the function.

```python
async def task_one():
    ...

async def task_two():
    ...

# or
import anyio
async with anyio.create_task_group() as task_group:
    task_group.start_soon(task_one)
    task_group.start_soon(task_two)
# or
import asyncer
async with asyncer.create_task_group() as task_group
    task_group.soonify(task_one)()
    task_group.soonify(task_one)()
# or 
import asyncio
await asyncio.gather(task_one(), task_two())
```

## Implement Caching

Caching is a practice of storing frequently used data or results in a location for quicker access in the future. By implementing caching, you can significantly reduce repetitive computations and database lookups, leading to faster response times. Python libraries like `cachetools` or `functools.lru_cache` are popular tools for caching, but those are sync-only.

For caching `async def` functions, S.T.A.R.K. ships its own `alru_cache`: an async LRU cache decorator with a TTL and built-in in-flight deduplication, two concurrent calls with the same arguments share one underlying call instead of running it twice.

```python
from stark.general.cache import alru_cache

@alru_cache(maxsize=128, ttl=60.0)
async def fetch_weather(city: str) -> str:
    ...  # only actually runs once per `city` within the TTL window
```

Useful anywhere a command calls a slow external API and the same query is likely to repeat (weather, search, lookups) within a short window.

---

Optimization is a continuous process. As Stark grows and evolves, always look out for opportunities to refine and streamline its operations. Remember, the key is to ensure Stark remains responsive and efficient, offering users a seamless and efficient voice assistant experience.
