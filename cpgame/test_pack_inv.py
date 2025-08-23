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


# Variant 2: 1 integer with bit packing
class BitPackedClass:
    __slots__ = ['_flags']

    def __init__(self):
        self._flags = 0

    @property
    def flag1(self):
        return bool(self._flags & 1)

    @flag1.setter
    def flag1(self, value):
        if bool(value):
            self._flags |= 1
        else:
            self._flags &= ~1

    @property
    def flag2(self):
        return bool(self._flags & 2)

    @flag2.setter
    def flag2(self, value):
        if bool(value):
            self._flags |= 2
        else:
            self._flags &= ~2

    @property
    def flag3(self):
        return bool(self._flags & 4)

    @flag3.setter
    def flag3(self, value):
        if bool(value):
            self._flags |= 4
        else:
            self._flags &= ~4

    @property
    def flag4(self):
        return bool(self._flags & 8)

    @flag4.setter
    def flag4(self, value):
        if bool(value):
            self._flags |= 8
        else:
            self._flags &= ~8

    @property
    def flag5(self):
        return bool(self._flags & 16)

    @flag5.setter
    def flag5(self, value):
        if bool(value):
            self._flags |= 16
        else:
            self._flags &= ~16

    @property
    def flag6(self):
        return bool(self._flags & 32)

    @flag6.setter
    def flag6(self, value):
        if bool(value):
            self._flags |= 32
        else:
            self._flags &= ~32

    @property
    def flag7(self):
        return bool(self._flags & 64)

    @flag7.setter
    def flag7(self, value):
        if bool(value):
            self._flags |= 64
        else:
            self._flags &= ~64

    @property
    def flag8(self):
        return bool(self._flags & 128)

    @flag8.setter
    def flag8(self, value):
        if bool(value):
            self._flags |= 128
        else:
            self._flags &= ~128

    def set_all_flags(self, values):
        self.flag1, self.flag2, self.flag3, self.flag4, self.flag5, self.flag6, self.flag7, self.flag8 = values

    def get_all_flags(self):
        return (self.flag1, self.flag2, self.flag3, self.flag4, self.flag5, self.flag6, self.flag7, self.flag8)


# Test function - BitPacked first, then Boolean
def test_memory_and_performance_inverted():
    print("Testing memory usage and performance (BitPacked first)...")

    # Test BitPackedClass first
    print("\n--- Testing BitPackedClass First ---")
    mem_before = mem_used()

    obj2 = BitPackedClass()
    _, time_taken = timeit(lambda: obj2.set_all_flags([True, False, True, False, True, False, True, False]))
    print(f"Set flags time: {time_taken:.6f}s")

    _, time_taken = timeit(lambda: obj2.get_all_flags())
    print(f"Get flags time: {time_taken:.6f}s")

    mem_after = mem_used()
    mem_used_bits = mem_after - mem_before
    print(f"Memory used by BitPackedClass: {mem_used_bits} bytes")

    # Test BooleanClass second
    print("\n--- Testing BooleanClass Second ---")
    mem_before = mem_used()

    obj1 = BooleanClass()
    _, time_taken = timeit(lambda: obj1.set_all_flags([True, False, True, False, True, False, True, False]))
    print(f"Set flags time: {time_taken:.6f}s")

    _, time_taken = timeit(lambda: obj1.get_all_flags())
    print(f"Get flags time: {time_taken:.6f}s")

    mem_after = mem_used()
    mem_used_bool = mem_after - mem_before
    print(f"Memory used by BooleanClass: {mem_used_bool} bytes")

    # Compare results
    print(f"\n--- Results ---")
    print(f"BitPackedClass memory: {mem_used_bits} bytes")
    print(f"BooleanClass memory: {mem_used_bool} bytes")
    print(f"Memory difference: {mem_used_bool - mem_used_bits} bytes")
    print(f"Bit packing saves: {((mem_used_bool - mem_used_bits) / mem_used_bool * 100):.1f}% of memory")


# Run the test
test_memory_and_performance_inverted()