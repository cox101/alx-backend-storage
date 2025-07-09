#!/usr/bin/env python3
""" Module to implement web caching and tracking using Redis """
import redis
import requests
from typing import Callable

r = redis.Redis()


def count_url_access(method: Callable) -> Callable:
    """Decorator to count URL accesses and cache results."""
    def wrapper(url: str) -> str:
        """Wrapper that tracks URL access and caches content."""
        cache_key = f"cached:{url}"
        count_key = f"count:{url}"

        r.incr(count_key)
        cached = r.get(cache_key)
        if cached:
            return cached.decode('utf-8')

        # Fetch and cache new content
        response = method(url)
        r.setex(cache_key, 10, response)
        return response
    return wrapper


@count_url_access
def get_page(url: str) -> str:
    """Get and return the HTML content of a URL."""
    response = requests.get(url)
    return response.text
