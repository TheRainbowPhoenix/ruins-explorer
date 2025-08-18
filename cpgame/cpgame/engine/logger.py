# cpgame/engine/logger.py
# A simple, platform-aware logger.

_IS_DESKTOP_PLATFORM = False
try:
    # This is a reliable check, since it's not part of MicroPython
    from typing import Any
    _IS_DESKTOP_PLATFORM = True
except ImportError:
    _IS_DESKTOP_PLATFORM = False

def log(*args, **kwargs):
    """
    Prints messages only when running on a desktop (CPython) environment.
    On MicroPython, this function does nothing.
    It accepts the same arguments as the built-in print() function.
    """
    if _IS_DESKTOP_PLATFORM:
        print(*args, **kwargs)
    else:
        pass