import gc
import time

# --- CONFIG ---
NUM = 100  # Number of instances to create (adjust down if memory tight)
DEBUG = True

def mem_used():
    gc.collect()
    return gc.mem_alloc()

def timeit(func):
    start = time.monotonic()
    result = func()
    end = time.monotonic()
    elapsed = end - start
    return result, elapsed

mem_used()

m_start = mem_used()

print(m_start)