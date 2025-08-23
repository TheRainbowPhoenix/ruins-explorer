import gc
import time


def mem_used():
    gc.collect()
    return gc.mem_alloc()


def timeit(func):
    start = time.monotonic()
    result = func()
    end = time.monotonic()
    elapsed = end - start
    return result, elapsed


# Variant 1: 8 separate boolean properties
class BooleanClass:
    __slots__ = ['flag1', 'flag2', 'flag3', 'flag4', 'flag5', 'flag6', 'flag7', 'flag8']

    def __init__(self):
        self.flag1 = False
        self.flag2 = False
        self.flag3 = False
        self.flag4 = False
        self.flag5 = False
        self.flag6 = False
        self.flag7 = False
        self.flag8 = False

    def set_all_flags(self, values):
        self.flag1, self.flag2, self.flag3, self.flag4, self.flag5, self.flag6, self.flag7, self.flag8 = values

    def get_all_flags(self):
        return self.flag1, self.flag2, self.flag3, self.flag4, self.flag5, self.flag6, self.flag7, self.flag8


# Test function
def test_memory_and_performance():
    print("Testing memory usage and performance...")
    print("\n--- Testing ---")
    mem_before = mem_used()

    obj1 = BooleanClass()
    _, time_taken = timeit(lambda: obj1.set_all_flags([True, False, True, False, True, False, True, False]))
    print(f"Set flags time: {time_taken:.6f}s")

    _, time_taken = timeit(lambda: obj1.get_all_flags())
    print(f"Get flags time: {time_taken:.6f}s")

    mem_after = mem_used()
    mem_used_bool = mem_after - mem_before
    print(f"Memory used: {mem_used_bool} bytes")

    # Compare results
    print(f"\n--- Results ---")
    print(f"memory: {mem_used_bool} bytes")
    return mem_used_bool


# Run the test
test_memory_and_performance()