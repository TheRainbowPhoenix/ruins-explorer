# cpgame/engine/profiler.py
# A lightweight memory profiling utility for debugging on constrained devices.

import gc
# from cpgame.engine.logger import log

# --- GLOBAL DEBUG FLAG ---
# Set this to False for "release" builds to disable all profiling.
DEBUG_MEMORY = True

class MemoryProfiler:
    """
    A context manager to profile memory usage of a block of code.
    Usage:
        with MemoryProfiler("Loading Assets"):
            # code to profile...
    """
    def __init__(self, name: str):
        self.name = name
        self.start_mem = 0

    def __enter__(self):
        if not DEBUG_MEMORY:
            return
        
        # Collect garbage before measuring to get a clean baseline
        gc.collect()
        self.start_mem = gc.mem_alloc()
        print("+{} {}B".format(self.name, self.start_mem))

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not DEBUG_MEMORY:
            return

        # Collect any garbage created within the block before the final measurement
        gc.collect()
        end_mem = gc.mem_alloc()
        delta = end_mem - self.start_mem
        
        print("-{} {}B = {}B".format(self.name, end_mem, delta))

def profile_memory(name: str):
    """Decorator version of the profiler (less flexible for our needs but good to have)."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            with MemoryProfiler(name):
                return func(*args, **kwargs)
        return wrapper
    return decorator