import gc
import time

# --- CONFIG ---
NUM = 100  # Number of instances to create (adjust down if memory tight)
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

print("=== Advanced Memory & Speed Benchmark ===\n")

# Warm up
mem_used()

# =============================================================================
# 1. Class with Static Property
# =============================================================================
print("1. Class with @staticmethod / @property:")

m_start = mem_used()
class StaticRect:
    __slots__ = ('x', 'y', 'w', 'h')

    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h

    @staticmethod
    def area(w, h):
        return w * h

    @property
    def center(self):
        return (self.x + self.w // 2, self.y + self.h // 2)

# Instance cost
m_mid = mem_used()
instances_static = [StaticRect(1, 2, 10, 10) for _ in range(NUM)]
m_end = mem_used()

mem_per = (m_end - m_mid) // NUM
_, time_us = timeit(lambda: [StaticRect(1,2,10,10) for _ in range(NUM)])

print(f"  {NUM} instances → {m_end - m_mid} bytes total")
print(f"  ~{mem_per} bytes per instance")
print(f"  Time: {time_us:,} μs")

del instances_static
mem_used()

# =============================================================================
# 2. Class holding objects (list/dict) in __init__
# =============================================================================
print("\n2. Class holding list/dict in __init__:")

m_start = mem_used()
class FatRect:
    def __init__(self, x, y, w, h):
        self.data = [x, y, w, h]         # List overhead
        self.meta = {'type': 'rect'}     # Dict overhead

m_mid = mem_used()
instances_fat = [FatRect(1,2,10,10) for _ in range(NUM)]
m_end = mem_used()

mem_per = (m_end - m_mid) // NUM
_, time_us = timeit(lambda: [FatRect(1,2,10,10) for _ in range(NUM)])

print(f"  {NUM} instances → {m_end - m_mid} bytes total")
print(f"  ~{mem_per} bytes per instance")
print(f"  Time: {time_us:,} μs")

del instances_fat
mem_used()

# =============================================================================
# 3. Original Rect class (with properties)
# =============================================================================
print("\n3. Original Rect class (properties, no __slots__):")

m_start = mem_used()
try:
    from typing import Tuple  # Assume exists or comment out if not available
except: pass

class Rect:
    """An integer-based rectangle defined by position and size."""
    def __init__(self, x: int, y: int, w: int, h: int):
        self.x, self.y, self.w, self.h = x, y, w, h
    
    @property
    def left(self) -> int:
        return self.x
    @property
    def right(self) -> int:
        return self.x + self.w
    @property
    def top(self) -> int:
        return self.y
    @property
    def bottom(self) -> int:
        return self.y + self.h

    def intersects(self, other: 'Rect') -> bool:
        return (self.right > other.left and self.left < other.right and
                self.bottom > other.top and self.top < other.top)

    @property
    def width(self) -> int:
        return self.w
    @property
    def height(self) -> int:
        return self.h

    @property
    def size(self) -> Tuple[int, int]:
        return (self.w, self.h)

m_mid = mem_used()
instances_rect = [Rect(1, 2, 10, 10) for _ in range(NUM)]
m_end = mem_used()

mem_per = (m_end - m_mid) // NUM
_, time_us = timeit(lambda: [Rect(1,2,10,10) for _ in range(NUM)])

print(f"  {NUM} instances → {m_end - m_mid} bytes total")
print(f"  ~{mem_per} bytes per instance")
print(f"  Time: {time_us:,} μs")

del instances_rect
mem_used()

# =============================================================================
# 4. Optimized PackedRect: store x,y,w,h in single 32-bit int (two 16-bit pairs)
#   Use: (x,y) in first int, (w,h) in second? Or pack all into one?
#   But: int32 can only hold 4x8-bit or 2x16-bit values.
#   Let's pack: x,y,w,h as 4x 8-bit → only for small values (<256)
# =============================================================================
print("\n4. PackedRect (8-bit values in one int):")

m_start = mem_used()
class PackedRect:
    __slots__ = ('data',)
    def __init__(self, x, y, w, h):
        # Pack four 8-bit values into one 32-bit int
        self.data = (int(x)&0xFF) | ((int(y)&0xFF)<<8) | ((int(w)&0xFF)<<16) | ((int(h)&0xFF)<<24)

    def unpack(self):
        d = self.data
        return d & 0xFF, (d >> 8) & 0xFF, (d >> 16) & 0xFF, (d >> 24) & 0xFF

    @property
    def x(self): return self.data & 0xFF
    @property
    def y(self): return (self.data >> 8) & 0xFF
    @property
    def w(self): return (self.data >> 16) & 0xFF
    @property
    def h(self): return (self.data >> 24) & 0xFF

    @property
    def right(self): return self.x + self.w
    @property
    def bottom(self): return self.y + self.h

    def intersects(self, other):
        return (self.right > other.x and self.x < other.right and
                self.bottom > other.y and self.y < other.bottom)

m_mid = mem_used()
instances_packed = [PackedRect(1,2,10,10) for _ in range(NUM)]
m_end = mem_used()

mem_per = (m_end - m_mid) // NUM
_, time_us = timeit(lambda: [PackedRect(1,2,10,10) for _ in range(NUM)])

print(f"  {NUM} instances → {m_end - m_mid} bytes total")
print(f"  ~{mem_per} bytes per instance")
print(f"  Time: {time_us:,} μs")

del instances_packed
mem_used()

# =============================================================================
# 5. Ultra-minimal: __slots__ + no properties, just direct access
# =============================================================================
print("\n5. MinimalRect (__slots__, direct access):")

m_start = mem_used()
class MinimalRect:
    __slots__ = ('x', 'y', 'w', 'h')
    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h

m_mid = mem_used()
instances_min = [MinimalRect(1,2,10,10) for _ in range(NUM)]
m_end = mem_used()

mem_per = (m_end - m_mid) // NUM
_, time_us = timeit(lambda: [MinimalRect(1,2,10,10) for _ in range(NUM)])

print(f"  {NUM} instances → {m_end - m_mid} bytes total")
print(f"  ~{mem_per} bytes per instance")
print(f"  Time: {time_us:,} μs")

# =============================================================================
# Final GC
# =============================================================================
gc.collect()
final_free = gc.mem_free()
print(f"\n--- Final ---\nFree memory: {final_free} bytes")