# Optimization for Stark

When it comes to Stark, or any software platform, optimization is pivotal to ensuring smooth and efficient operations. Here are some pivotal guidelines and best practices to ensure that Stark runs at its best:

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

Caching is a practice of storing frequently used data or results in a location for quicker access in the future. By implementing caching, you can significantly reduce repetitive computations and database lookups, leading to faster response times. Python libraries like `cachetools` or `functools.lru_cache` are popular tools for caching.

---

Optimization is a continuous process. As Stark grows and evolves, always look out for opportunities to refine and streamline its operations. Remember, the key is to ensure Stark remains responsive and efficient, offering users a seamless and efficient voice assistant experience.
