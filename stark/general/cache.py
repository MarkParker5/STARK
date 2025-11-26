from collections import OrderedDict
from functools import wraps
from typing import Awaitable, Callable

import anyio

type Seconds = float


def alru_cache[**P, T](maxsize: int = 128, ttl: Seconds = 60.0) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
    def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        cache: OrderedDict[tuple, tuple[T, float]] = OrderedDict()
        in_flight: dict[tuple, anyio.Event] = {}
        lock = anyio.Lock()

        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            key = (args, tuple(sorted(kwargs.items())))

            while True:
                async with lock:
                    now = anyio.current_time()

                    if key in cache:
                        value, ts = cache[key]
                        if now - ts < ttl:
                            cache.move_to_end(key)
                            return value
                        cache.pop(key)

                    if key in in_flight:
                        ev = in_flight[key]
                    else:
                        ev = anyio.Event()
                        in_flight[key] = ev
                        break

                await ev.wait()

            try:
                result: T = await func(*args, **kwargs)
            finally:
                async with lock:
                    ev = in_flight.pop(key, None)
                    if ev:
                        ev.set()

            async with lock:
                cache[key] = (result, anyio.current_time())
                cache.move_to_end(key)
                if len(cache) > maxsize:
                    cache.popitem(last=False)

            return result

        return wrapper

    return decorator
