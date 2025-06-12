__all__ = [
    "lock_decorator",
]

def lock_decorator(func):
    async def wrapper(self, *args, **kwargs):
        with self._lock:
            result = await func(self, *args, **kwargs)
            return result

    return wrapper
