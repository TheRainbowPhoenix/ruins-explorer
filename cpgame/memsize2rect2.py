import gc
import time

try:
    import ustruct as struct
except ImportError:
    import struct

try:
    import collections
    NamedTupleRect = collections.namedtuple('NamedTupleRect', ['x', 'y', 'w', 'h'])
except ImportError:
    NamedTupleRect = None

try:
    import types
except ImportError:
    types = None

try:
    import array
except ImportError:
    array = None

# --- CONFIG ---
NUM = 100
DEBUG = True

def mem_used():
    gc.collect()
    return gc.mem_alloc()

def timeit(func):
    start = time.ticks_us()
    result = func()
    end = time.ticks_us()
    elapsed = time.ticks_diff(end, start)
    return result, elapsed

print("=== Class vs Lightweight Data Types Benchmark ===\n")

# Warm up
mem_used()

# =============================================================================
# 1. Minimal Class (baseline with __slots__)
# =============================================================================
print("1. MinimalRect (class + __slots__):")

class MinimalRect:
    __slots__ = ('x', 'y', 'w', 'h')
    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h

m_start = mem_used()
instances = [MinimalRect(1,2,10,10) for _ in range(NUM)]
m_end = mem_used()
mem_per = (m_end - m_start) // NUM
_, time_us = timeit(lambda: [MinimalRect(1,2,10,10) for _ in range(NUM)])
print(f"  {NUM} → {m_end - m_start} B | ~{mem_per} B/obj | {time_us:,} μs")

del instances
mem_used()

# =============================================================================
# 2. namedtuple
# =============================================================================
if NamedTupleRect:
    print("\n2. namedtuple('x', 'y', 'w', 'h'):")

    m_start = mem_used()
    instances = [NamedTupleRect(1,2,10,10) for _ in range(NUM)]
    m_end = mem_used()
    mem_per = (m_end - m_start) // NUM
    _, time_us = timeit(lambda: [NamedTupleRect(1,2,10,10) for _ in range(NUM)])

    print(f"  {NUM} → {m_end - m_start} B | ~{mem_per} B/obj | {time_us:,} μs")
else:
    print("\n2. namedtuple: X Not available (no 'collections')")

# =============================================================================
# 3. Plain tuple
# =============================================================================
print("\n3. Plain tuple (x,y,w,h):")

m_start = mem_used()
instances = [(1, 2, 10, 10) for _ in range(NUM)]
m_end = mem_used()
mem_per = (m_end - m_start) // NUM
_, time_us = timeit(lambda: [(1, 2, 10, 10) for _ in range(NUM)])

print(f"  {NUM} → {m_end - m_start} B | ~{mem_per} B/obj | {time_us:,} μs")

del instances
mem_used()

# =============================================================================
# 4. Dictionary
# =============================================================================
print("\n4. Dict {'x':1, 'y':2, 'w':10, 'h':10}:")

m_start = mem_used()
instances = [{'x':1, 'y':2, 'w':10, 'h':10} for _ in range(NUM)]
m_end = mem_used()
mem_per = (m_end - m_start) // NUM
_, time_us = timeit(lambda: [{'x':1, 'y':2, 'w':10, 'h':10} for _ in range(NUM)])

print(f"  {NUM} → {m_end - m_start} B | ~{mem_per} B/obj | {time_us:,} μs")

del instances
mem_used()

# =============================================================================
# 5. SimpleNamespace (like dynamic object)
# =============================================================================
if types and hasattr(types, 'SimpleNamespace'):
    print("\n5. SimpleNamespace(x=1, y=2, w=10, h=10):")

    m_start = mem_used()
    instances = [types.SimpleNamespace(x=1, y=2, w=10, h=10) for _ in range(NUM)]
    m_end = mem_used()
    mem_per = (m_end - m_start) // NUM
    _, time_us = timeit(lambda: [types.SimpleNamespace(x=1, y=2, w=10, h=10) for _ in range(NUM)])

    print(f"  {NUM} → {m_end - m_start} B | ~{mem_per} B/obj | {time_us:,} μs")
else:
    print("\n5. SimpleNamespace: X Not available")

# =============================================================================
# 6. array.array of ints (compact storage for many rects)
#   Store all data in one big array: [x,y,w,h, x,y,w,h, ...]
#   One array for 10k rects = 40k ints = 40k * 2 or 4 bytes
# =============================================================================
if array:
    print("\n6. array.array('h') [int16] for all rects (bulk storage):")

    # Simulate storing 10k rects in one flat array
    m_start = mem_used()
    flat = array.array('h')  # int16, 2 bytes per value
    for _ in range(NUM):
        flat.extend([1, 2, 10, 10])
    m_end = mem_used()

    total_bytes = m_end - m_start
    per_rect = total_bytes // NUM
    _, time_us = timeit(lambda: array.array('h', sum(([1,2,10,10] for _ in range(NUM)), [])))

    print(f"  {NUM} → {total_bytes} B | ~{per_rect} B/rect | {time_us:,} μs")
    print(f"  (array overhead: ~{m_end - m_start - NUM*4*2} B)")
else:
    print("\n6. array.array: X Not available")

# =============================================================================
# 7. ustruct.pack into bytes (ultra-compact, read-only)
#   Pack each rect into 8 bytes: 4x int16 → 'hhhh'
# =============================================================================
print("\n7. struct.pack('hhhh', x,y,w,h) → bytes:")

m_start = mem_used()
instances = [struct.pack('hhhh', 1, 2, 10, 10) for _ in range(NUM)]
m_end = mem_used()
mem_per = (m_end - m_start) // NUM
_, time_us = timeit(lambda: [struct.pack('hhhh', 1, 2, 10, 10) for _ in range(NUM)])

print(f"  {NUM} → {m_end - m_start} B | ~{mem_per} B/obj | {time_us:,} μs")
print("  (read-only! unpack with struct.unpack)")

del instances
mem_used()

# =============================================================================
# Final Report
# =============================================================================
gc.collect()
final_free = gc.mem_free()
print(f"\n--- Summary ---")
print(f"Free RAM after test: {final_free} bytes")