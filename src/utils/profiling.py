"""Memory profiling utilities for Kore application."""

from __future__ import annotations

import gc
import logging
import os
import tracemalloc
from typing import Callable

logger = logging.getLogger(__name__)


def get_memory_usage() -> dict[str, float]:
    """Get current memory usage statistics.

    Returns:
        Dictionary with memory usage information in MB.
    """
    try:
        import psutil

        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()

        return {
            "rss_mb": memory_info.rss / 1024 / 1024,  # Resident Set Size
            "vms_mb": memory_info.vms / 1024 / 1024,  # Virtual Memory Size
        }
    except ImportError:
        # Fallback to basic measurement if psutil not available
        logger.warning("psutil not available, using basic memory measurement")
        return {"rss_mb": 0.0, "vms_mb": 0.0}


def start_memory_tracking() -> None:
    """Start memory tracking with tracemalloc."""
    tracemalloc.start()
    logger.info("Memory tracking started")


def stop_memory_tracking() -> dict[str, float]:
    """Stop memory tracking and return statistics.

    Returns:
        Dictionary with memory statistics.
    """
    if not tracemalloc.is_tracing():
        logger.warning("Memory tracking was not started")
        return {"current_mb": 0.0, "peak_mb": 0.0}

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    stats = {
        "current_mb": current / 1024 / 1024,
        "peak_mb": peak / 1024 / 1024,
    }

    logger.info(f"Memory tracking stopped. Current: {stats['current_mb']:.2f} MB, Peak: {stats['peak_mb']:.2f} MB")
    return stats


def profile_memory(func: Callable) -> Callable:
    """Decorator to profile memory usage of a function.

    Args:
        func: Function to profile.

    Returns:
        Wrapped function that logs memory usage.
    """

    def wrapper(*args: object, **kwargs: object) -> object:
        gc.collect()
        start_memory = get_memory_usage()

        result = func(*args, **kwargs)

        gc.collect()
        end_memory = get_memory_usage()

        memory_diff = end_memory["rss_mb"] - start_memory["rss_mb"]
        logger.info(
            f"Memory usage for {func.__name__}: {memory_diff:.2f} MB "
            f"(Start: {start_memory['rss_mb']:.2f} MB, End: {end_memory['rss_mb']:.2f} MB)"
        )

        return result

    return wrapper


def log_memory_snapshot(label: str = "Memory Snapshot") -> None:
    """Log current memory usage snapshot.

    Args:
        label: Label for the snapshot.
    """
    memory = get_memory_usage()
    logger.info(f"{label}: RSS={memory['rss_mb']:.2f} MB, VMS={memory['vms_mb']:.2f} MB")
