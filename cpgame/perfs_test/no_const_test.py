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


# Constants defined without const (regular variables)
FLAG1 = 1
FLAG2 = 2
FLAG3 = 4
FLAG4 = 8
FLAG5 = 16
FLAG6 = 32
FLAG7 = 64
FLAG8 = 128

class NoConstClass:
    __slots__ = ['_flags']

    def __init__(self):
        self._flags = 0

    @property
    def flag1(self):
        return bool(self._flags & FLAG1)

    @flag1.setter
    def flag1(self, value):
        if bool(value):
            self._flags |= FLAG1
        else:
            self._flags &= ~FLAG1

    @property
    def flag2(self):
        return bool(self._flags & FLAG2)

    @flag2.setter
    def flag2(self, value):
        if bool(value):
            self._flags |= FLAG2
        else:
            self._flags &= ~FLAG2

    @property
    def flag3(self):
        return bool(self._flags & FLAG3)

    @flag3.setter
    def flag3(self, value):
        if bool(value):
            self._flags |= FLAG3
        else:
            self._flags &= ~FLAG3

    @property
    def flag4(self):
        return bool(self._flags & FLAG4)

    @flag4.setter
    def flag4(self, value):
        if bool(value):
            self._flags |= FLAG4
        else:
            self._flags &= ~FLAG4

    @property
    def flag5(self):
        return bool(self._flags & FLAG5)

    @flag5.setter
    def flag5(self, value):
        if bool(value):
            self._flags |= FLAG5
        else:
            self._flags &= ~FLAG5

    @property
    def flag6(self):
        return bool(self._flags & FLAG6)

    @flag6.setter
    def flag6(self, value):
        if bool(value):
            self._flags |= FLAG6
        else:
            self._flags &= ~FLAG6

    @property
    def flag7(self):
        return bool(self._flags & FLAG7)

    @flag7.setter
    def flag7(self, value):
        if bool(value):
            self._flags |= FLAG7
        else:
            self._flags &= ~FLAG7

    @property
    def flag8(self):
        return bool(self._flags & FLAG8)

    @flag8.setter
    def flag8(self, value):
        if bool(value):
            self._flags |= FLAG8
        else:
            self._flags &= ~FLAG8

    def set_all_flags(self, values):
        self.flag1, self.flag2, self.flag3, self.flag4, self.flag5, self.flag6, self.flag7, self.flag8 = values

    def get_all_flags(self):
        return (self.flag1, self.flag2, self.flag3, self.flag4, self.flag5, self.flag6, self.flag7, self.flag8)


# Test function
def test_memory_and_performance():
    print("Testing memory usage and performance without const...")

    # Test NoConstClass
    print("\n--- Testing NoConstClass ---")
    mem_before = mem_used()

    obj = NoConstClass()
    _, time_taken = timeit(lambda: obj.set_all_flags([True, False, True, False, True, False, True, False]))
    print(f"Set flags time: {time_taken:.6f}s")

    _, time_taken = timeit(lambda: obj.get_all_flags())
    print(f"Get flags time: {time_taken:.6f}s")

    mem_after = mem_used()
    mem_used_no_const = mem_after - mem_before
    print(f"Memory used by NoConstClass: {mem_used_no_const} bytes")

    # Compare results
    print(f"\n--- Results ---")
    print(f"NoConstClass memory: {mem_used_no_const} bytes")
    return mem_used_no_const


# Run the test
test_memory_and_performance()