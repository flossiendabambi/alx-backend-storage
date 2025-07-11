#!/usr/bin/env python3
"""
Module to cache web page content with expiration and track URL access count.
"""

import redis
import requests
from functools import wraps
from typing import Callable

# Initialize Redis client
r = redis.Redis()


def count_url_access(method: Callable) -> Callable:
    """
    Decorator to count how many times a URL has been accessed.
    Stores count in Redis with key pattern 'count:{url}'.
    """
    @wraps(method)
    def wrapper(url: str) -> str:
        key = f"count:{url}"
        r.incr(key)
        return method(url)
    return wrapper


def cache_page(expire: int = 10) -> Callable:
    """
    Decorator to cache the page content in Redis with expiration (seconds).
    Cache key is the URL.
    """
    def decorator(method: Callable) -> Callable:
        @wraps(method)
        def wrapper(url: str) -> str:
            cached = r.get(url)
            if cached:
                return cached.decode("utf-8")
            result = method(url)
            r.setex(url, expire, result)
            return result
        return wrapper
    return decorator


@count_url_access
@cache_page(expire=10)
def get_page(url: str) -> str:
    """
    Fetches the HTML content of a URL using requests.
    Caches the response for 10 seconds and tracks access count.
    """
    response = requests.get(url)
    response.raise_for_status()
    return response.text
