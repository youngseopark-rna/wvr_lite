import logging
import time
from functools import wraps

import sys

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

if not root_logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("[%(levelname)s] %(asctime)s - %(message)s"))
    root_logger.addHandler(handler)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def __handle_exception(is_success: bool = True):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            try:
                result = func(*args, **kwargs)

                end_time = time.perf_counter()
                elapsed_time = end_time - start_time
                logger.info(
                    f"Test Success: {func.__name__} took {elapsed_time:.4f} seconds"
                )

                return result
            except Exception as e:
                is_success = False
                logger.error(f"{is_success}, Test Failed: {e}")
                raise e

        return wrapper

    return decorator
