from functools import wraps
import asyncio
from typing import Callable, Any
import logging

logger = logging.getLogger(__name__)

def background_task(func: Callable) -> Callable:
    """Decorator to run a function as a background task"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(func(*args, **kwargs))
        except RuntimeError:
            # No running loop, create one
            asyncio.run(func(*args, **kwargs))
        except Exception as e:
            logger.error(f"Background task failed: {e}")
    return wrapper