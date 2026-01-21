from typing import Callable
from functools import wraps

def register_function(register:dict[str, Callable], func_alias:str):
    def decorator(func:Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        register[func_alias] = func

        return wrapper
    return decorator
