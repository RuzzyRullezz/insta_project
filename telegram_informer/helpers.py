import functools
import sys
import os


def terminate_wrapper(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, *kwargs)
        except BaseException:
            sys.excepthook(*sys.exc_info())
            os._exit(-1)
    return wrapper
