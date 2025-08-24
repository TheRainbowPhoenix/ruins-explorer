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


# Import const from micropython
from micropython import const

# Constants defined with const
CONST_FLAG1 = const(1)
CONST_FLAG2 = const(2)
CONST_FLAG3 = const(4)
CONST_FLAG4 = const(8)
CONST_FLAG5 = const(16)
CONST_FLAG6 = const(32)
CONST_FLAG7 = const(64)
CONST_FLAG8 = const(128)

class ConstClass:
    __slots__ = ['_flags']

    def __init__(self):
        self._flags = 0

    @property
    def flag1(self):
        return bool(self._flags & CONST_FLAG1)

    @flag1.setter
    def flag1(self, value):
        if bool(value):
            self._flags |= CONST_FLAG1
        else:
            self._flags &= ~CONST_FLAG1

    @property
    def flag2(self):
        return bool(self._flags & CONST_FLAG2)

    @flag2.setter
    def flag2(self, value):
        if bool(value):
            self._flags |= CONST_FLAG2
        else:
            self._flags &= ~CONST_FLAG2

    @property
    def flag3(self):
        return bool(self._flags & CONST_FLAG3)

    @flag3.setter
    def flag3(self, value):
        if bool(value):
            self._flags |= CONST_FLAG3
        else:
            self._flags &= ~CONST_FLAG3

    @property
    def flag4(self):
        return bool(self._flags & CONST_FLAG4)

    @flag4.setter
    def flag4(self, value):
        if bool(value):
            self._flags |= CONST_FLAG4
        else:
            self._flags &= ~CONST_FLAG4

    @property
    def flag5(self):
        return bool(self._flags & CONST_FLAG5)

    @flag5.setter
    def flag5(self, value):
        if bool(value):
            self._flags |= CONST_FLAG5
        else:
            self._flags &= ~CONST_FLAG5

    @property
    def flag6(self):
        return bool(self._flags & CONST_FLAG6)

    @flag6.setter
    def flag6(self, value):
        if bool(value):
            self._flags |= CONST_FLAG6
        else:
            self._flags &= ~CONST_FLAG6

    @property
    def flag7(self):
        return bool(self._flags & CONST_FLAG7)

    @flag7.setter
    def flag7(self, value):
        if bool(value):
            self._flags |= CONST_FLAG7
        else:
            self._flags &= ~CONST_FLAG7

    @property
    def flag8(self):
        return bool(self._flags & CONST_FLAG8)

    @flag8.setter
    def flag8(self, value):
        if bool(value):
            self._flags |= CONST_FLAG8
        else:
            self._flags &= ~CONST_FLAG8

    def set_all_flags(self, values):
        self.flag1, self.flag2, self.flag3, self.flag4, self.flag5, self.flag6, self.flag7, self.flag8 = values

    def get_all_flags(self):
        return (self.flag1, self.flag2, self.flag3, self.flag4, self.flag5, self.flag6, self.flag7, self.flag8)


# Test function
def test_memory_and_performance():
    print("Testing memory usage and performance with const...")

    # Test ConstClass
    print("\n--- Testing ConstClass ---")
    mem_before = mem_used()

    obj = ConstClass()
    _, time_taken = timeit(lambda: obj.set_all_flags([True, False, True, False, True, False, True, False]))
    print(f"Set flags time: {time_taken:.6f}s")

    _, time_taken = timeit(lambda: obj.get_all_flags())
    print(f"Get flags time: {time_taken:.6f}s")

    mem_after = mem_used()
    mem_used_const = mem_after - mem_before
    print(f"Memory used by ConstClass: {mem_used_const} bytes")

    # Compare results
    print(f"\n--- Results ---")
    print(f"ConstClass memory: {mem_used_const} bytes")
    return mem_used_const


# Run the test
test_memory_and_performance()