"""Utility decorators for Kore application."""

from __future__ import annotations

import functools
import logging
import time
from typing import Callable, TypeVar

F = TypeVar("F", bound=Callable)

logger = logging.getLogger(__name__)


def retry_on_failure(
    max_retries: int = 3,
    delay: float = 2.0,
    backoff_factor: float = 2.0,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable[[F], F]:
    """Decorator to retry a function on failure with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts.
        delay: Initial delay between retries in seconds.
        backoff_factor: Multiplier for delay after each retry.
        exceptions: Tuple of exception types to catch and retry on.

    Returns:
        Decorated function that will retry on failure.

    Example:
        @retry_on_failure(max_retries=3, delay=1.0)
        def fetch_data(url: str) -> dict:
            # Network request that might fail
            pass
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: object, **kwargs: object) -> object:
            current_delay = delay
            last_exception: Exception | None = None

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_retries - 1:
                        logger.error(
                            f"Function {func.__name__} failed after {max_retries} attempts: {e}"
                        )
                        raise

                    logger.warning(
                        f"Attempt {attempt + 1}/{max_retries} failed for {func.__name__}: {e}. "
                        f"Retrying in {current_delay:.1f}s..."
                    )
                    time.sleep(current_delay)
                    current_delay *= backoff_factor

            # This should never be reached, but mypy needs it
            if last_exception:
                raise last_exception
            raise RuntimeError("Unexpected error in retry decorator")

        return wrapper  # type: ignore[return-value]

    return decorator
