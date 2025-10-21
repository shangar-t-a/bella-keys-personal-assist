"""Time profiling utility for measuring execution time of function."""

import time
from functools import wraps

from utilities.logger import GetAppLogger


def log_exec_time(func):
    """Decorator to measure the execution time of a function."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = GetAppLogger(fallback_name="TimeProfile").get_logger()
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        logger.debug(f"Execution time for {func.__name__}: {execution_time:.2f} seconds")
        return result

    return wrapper


def async_log_exec_time(func):
    """Async decorator to measure the execution time of an async function."""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        logger = GetAppLogger(fallback_name="TimeProfile").get_logger()
        start_time = time.perf_counter()
        result = await func(*args, **kwargs)
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        logger.debug(f"Execution time for {func.__name__}: {execution_time:.2f} seconds")
        return result

    return wrapper


if __name__ == "__main__":
    import asyncio

    @log_exec_time
    def sample_function(duration):
        """Sample function that sleeps for a given duration."""
        time.sleep(duration)
        return "Function complete"

    print(sample_function(2))

    @async_log_exec_time
    async def sample_async_function(duration):
        """Sample async function that sleeps for a given duration."""
        await asyncio.sleep(duration)
        return "Async function complete"

    print(asyncio.run(sample_async_function(3)))
