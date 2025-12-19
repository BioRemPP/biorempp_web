"""
Logging Decorators

Provides reusable decorators for automatic logging.
"""

import functools
import logging
import time
from typing import Any, Callable, Optional


def log_execution(
    logger: Optional[logging.Logger] = None,
    level: int = logging.DEBUG,
    include_args: bool = False,
    include_result: bool = False,
):
    """
    Decorator to log function execution.

    Logs function entry, execution time, and completion/failure.

    Parameters
    ----------
    logger : Optional[logging.Logger]
        Logger to use (defaults to function's module logger)
    level : int
        Log level to use (default: DEBUG)
    include_args : bool
        Whether to log function arguments (default: False)
    include_result : bool
        Whether to log function result (default: False)

    Returns
    -------
    Callable
        Decorated function

    Examples
    --------
    >>> @log_execution(level=logging.INFO, include_args=True)
    ... def process_sample(sample_id: str):
    ...     return f"Processed {sample_id}"
    >>>
    >>> result = process_sample("S001")
    INFO - Entering process_sample with args=('S001',), kwargs={}
    INFO - Completed process_sample in 0.12ms
    """

    def decorator(func: Callable) -> Callable:
        nonlocal logger
        if logger is None:
            logger = logging.getLogger(func.__module__)

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            func_name = func.__qualname__

            # Log entry
            log_msg = f"Entering {func_name}"
            if include_args:
                log_msg += f" with args={args}, kwargs={kwargs}"
            logger.log(level, log_msg)

            start_time = time.time()

            try:
                result = func(*args, **kwargs)

                # Log success
                duration = (time.time() - start_time) * 1000  # ms
                log_msg = f"Completed {func_name} in {duration:.2f}ms"
                if include_result:
                    log_msg += f" with result={result}"
                logger.log(level, log_msg)

                return result

            except Exception as e:
                # Log error
                duration = (time.time() - start_time) * 1000
                logger.error(
                    f"Failed {func_name} after {duration:.2f}ms: {e}",
                    exc_info=True,
                )
                raise

        return wrapper

    return decorator


def log_performance(
    threshold_ms: float = 1000.0,
    logger: Optional[logging.Logger] = None,
):
    """
    Decorator to log slow function executions.

    Only logs if execution time exceeds threshold.

    Parameters
    ----------
    threshold_ms : float
        Threshold in milliseconds (default: 1000ms)
    logger : Optional[logging.Logger]
        Logger to use (defaults to function's module logger)

    Returns
    -------
    Callable
        Decorated function

    Examples
    --------
    >>> @log_performance(threshold_ms=500)
    ... def slow_operation():
    ...     time.sleep(1)
    >>>
    >>> slow_operation()
    WARNING - Slow execution: slow_operation took 1001.23ms (threshold: 500ms)
    """

    def decorator(func: Callable) -> Callable:
        nonlocal logger
        if logger is None:
            logger = logging.getLogger(func.__module__)

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            result = func(*args, **kwargs)
            duration = (time.time() - start_time) * 1000

            if duration > threshold_ms:
                msg = (
                    f"Slow execution: {func.__qualname__} took {duration:.2f}ms "
                    f"(threshold: {threshold_ms}ms)"
                )
                logger.warning(msg)

            return result

        return wrapper

    return decorator


def log_exceptions(
    logger: Optional[logging.Logger] = None,
    reraise: bool = True,
    level: int = logging.ERROR,
):
    """
    Decorator to automatically log exceptions.

    Parameters
    ----------
    logger : Optional[logging.Logger]
        Logger to use (defaults to function's module logger)
    reraise : bool
        Whether to reraise the exception after logging (default: True)
    level : int
        Log level to use (default: ERROR)

    Returns
    -------
    Callable
        Decorated function

    Examples
    --------
    >>> @log_exceptions()
    ... def risky_operation():
    ...     raise ValueError("Something went wrong")
    >>>
    >>> risky_operation()
    ERROR - Exception in risky_operation: Something went wrong
    Traceback (most recent call last):
    ...
    ValueError: Something went wrong
    """

    def decorator(func: Callable) -> Callable:
        nonlocal logger
        if logger is None:
            logger = logging.getLogger(func.__module__)

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.log(
                    level,
                    f"Exception in {func.__qualname__}: {e}",
                    exc_info=True,
                )
                if reraise:
                    raise

        return wrapper

    return decorator


def log_method_calls(
    logger: Optional[logging.Logger] = None,
    level: int = logging.DEBUG,
):
    """
    Class decorator to log all method calls.

    Automatically logs entry/exit of all public methods in a class.

    Parameters
    ----------
    logger : Optional[logging.Logger]
        Logger to use
    level : int
        Log level to use (default: DEBUG)

    Returns
    -------
    Callable
        Decorated class

    Examples
    --------
    >>> @log_method_calls(level=logging.INFO)
    ... class SampleProcessor:
    ...     def process(self, sample_id):
    ...         return f"Processed {sample_id}"
    """

    def decorator(cls):
        for attr_name in dir(cls):
            # Skip private/magic methods
            if attr_name.startswith("_"):
                continue

            attr = getattr(cls, attr_name)
            if callable(attr):
                # Wrap method with logging
                setattr(
                    cls,
                    attr_name,
                    log_execution(logger=logger, level=level)(attr),
                )

        return cls

    return decorator
