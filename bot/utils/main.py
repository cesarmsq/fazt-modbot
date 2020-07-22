"""
Copyright 2020 Fazt Community ~ All rights reserved. MIT license.
"""

from collections import Callable


def to_bool(s: str) -> bool:
    return s.lower() in ("1", "true", "on") if s else False


def to_str_bool(b: bool) -> str:
    if b is True:
        return "1"
    return "0"


def callback(func: Callable, *args, **kwargs) -> Callable:
    async def inner(*_, **__):
        return await func(*args, **kwargs)

    return inner
