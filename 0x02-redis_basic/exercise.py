#!/usr/bin/env python3
""" Redis basic module for caching and tracking """
import redis
import uuid
from typing import Union, Callable, Optional
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """Decorator to count the number of times a method is called."""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """Wrapper that increments the call count in Redis."""
        self._redis.incr(method.__qualname__)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """Decorator to store the history of inputs and outputs."""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """Store inputs and outputs in Redis."""
        key_input = method.__qualname__ + ":inputs"
        key_output = method.__qualname__ + ":outputs"

        self._redis.rpush(key_input, str(args))
        result = method(self, *args, **kwargs)
        self._redis.rpush(key_output, str(result))
        return result
    return wrapper


def replay(method: Callable):
    """Display the history of calls of a particular function."""
    r = redis.Redis()
    qualname = method.__qualname__
    inputs = r.lrange(f"{qualname}:inputs", 0, -1)
    outputs = r.lrange(f"{qualname}:outputs", 0, -1)
    print(f"{qualname} was called {len(inputs)} times:")
    for inp, outp in zip(inputs, outputs):
        print(f"{qualname}(*{inp.decode()}) -> {outp.decode()}")


class Cache:
    """Cache class for interacting with Redis."""

    def __init__(self):
        """Initialize Redis connection and flush data."""
        self._redis = redis.Redis()
        self._redis.flushdb()

    @call_history
    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """Store data in Redis using a random key and return the key."""
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self,
            key: str,
            fn: Optional[Callable] = None) -> Union[str, bytes, int, float, None]:
        """Retrieve data from Redis and optionally apply a conversion function."""
        data = self._redis.get(key)
        if data is None:
            return None
        return fn(data) if fn else data

    def get_str(self, key: str) -> str:
        """Retrieve a UTF-8 string from Redis."""
        return self.get(key, lambda d: d.decode("utf-8"))

    def get_int(self, key: str) -> int:
        """Retrieve an integer from Redis."""
        return self.get(key, int)
