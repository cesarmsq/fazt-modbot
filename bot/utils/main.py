def to_bool(s: str):
    return s.lower() in ('1', 'true', 'on') if s else False


def to_str_bool(b: bool):
    if b is True:
        return '1'
    return '0'


def callback(func, *args, **kwargs):
    async def inner(*_, **__):
        return await func(*args, **kwargs)
    return inner
