import gc

# --- CONFIG ---
DEBUG = True
NUM_ITEMS = 10  # Number of items to test scaling (must be >=1)

def m0():
    """Return current allocated memory after GC."""
    gc.collect()
    return gc.mem_alloc()

print("=== MicroPython Memory Usage Benchmark ===")
print("Measuring memory impact of common objects\n")

# Warm-up GC
m0()

# =============================================================================
# 1. Empty Class (definition only)
# =============================================================================
print("1. Empty class definition:")
m_start = m0()
class Dummy:
    pass
m_end = m0()
print(f"  Cost: {m_end - m_start} bytes")

# =============================================================================
# 2. Class Instance
# =============================================================================
print("\n2. Class instance (Dummy()):")
m_start = m0()
instances = [Dummy() for _ in range(NUM_ITEMS)]
m_end = m0()
per_instance = (m_end - m_start) // NUM_ITEMS
print(f"  {NUM_ITEMS} instances → {m_end - m_start} bytes total")
print(f"  ~{per_instance} bytes per instance")

del instances
m0()

# =============================================================================
# 3. Lambda
# =============================================================================
print("\n3. Lambda function (lambda x: x):")
m_start = m0()
lambdas = [lambda x: x for _ in range(NUM_ITEMS)]
m_end = m0()
per_lambda = (m_end - m_start) // NUM_ITEMS
print(f"  {NUM_ITEMS} lambdas → {m_end - m_start} bytes total")
print(f"  ~{per_lambda} bytes per lambda")

del lambdas
m0()

# =============================================================================
# 4. Regular Function
# =============================================================================
print("\n4. Regular function def f(x): return x:")
m_start = m0()

def make_func():
    def f(x):
        return x
    return f

functions = [make_func() for _ in range(NUM_ITEMS)]
m_end = m0()
per_func = (m_end - m_start) // NUM_ITEMS
print(f"  {NUM_ITEMS} functions → {m_end - m_start} bytes total")
print(f"  ~{per_func} bytes per function")

del functions
m0()

# =============================================================================
# 5. Integer (small int, e.g. 42)
# =============================================================================
print("\n5. Integer (small, e.g. 42):")
m_start = m0()
ints = [42 for _ in range(NUM_ITEMS)]
m_end = m0()
per_int = (m_end - m_start) // NUM_ITEMS
print(f"  {NUM_ITEMS} ints → {m_end - m_start} bytes total")
print(f"  ~{per_int} bytes per int")

del ints
m0()

# =============================================================================
# 6. String (short: 'abc')
# =============================================================================
print("\n6. Short string ('abc'):")
m_start = m0()
strings_short = ['abc' for _ in range(NUM_ITEMS)]
m_end = m0()
per_str_short = (m_end - m_start) // NUM_ITEMS
print(f"  {NUM_ITEMS} short strs → {m_end - m_start} bytes total")
print(f"  ~{per_str_short} bytes per short string")

del strings_short
m0()

# =============================================================================
# 7. String (long: 100 chars)
# =============================================================================
print("\n7. Long string (~100 chars):")
long_str = "x" * 100
m_start = m0()
long_strings = [long_str for _ in range(NUM_ITEMS)]
m_end = m0()
per_long_str = (m_end - m_start) // NUM_ITEMS
print(f"  {NUM_ITEMS} long strs → {m_end - m_start} bytes total")
print(f"  ~{per_long_str} bytes per ~100-char string")

del long_strings
m0()

# =============================================================================
# 8. Bytes (b'abc')
# =============================================================================
print("\n8. Bytes object (b'abc'):")
m_start = m0()
byte_objects = [b'abc' for _ in range(NUM_ITEMS)]
m_end = m0()
per_bytes = (m_end - m_start) // NUM_ITEMS
print(f"  {NUM_ITEMS} bytes → {m_end - m_start} bytes total")
print(f"  ~{per_bytes} bytes per bytes object")

del byte_objects
m0()

# =============================================================================
# 9. Tuple (small: (1,2))
# =============================================================================
print("\n9. Small tuple (2-item):")
m_start = m0()
tuples = [(1, 2) for _ in range(NUM_ITEMS)]
m_end = m0()
per_tuple = (m_end - m_start) // NUM_ITEMS
print(f"  {NUM_ITEMS} tuples → {m_end - m_start} bytes total")
print(f"  ~{per_tuple} bytes per tuple")

del tuples
m0()

# =============================================================================
# 10. List (empty [])
# =============================================================================
print("\n10. Empty list ([]):")
m_start = m0()
lists = [[] for _ in range(NUM_ITEMS)]
m_end = m0()
per_list = (m_end - m_start) // NUM_ITEMS
print(f"  {NUM_ITEMS} empty lists → {m_end - m_start} bytes total")
print(f"  ~{per_list} bytes per list")

del lists
m0()

# =============================================================================
# 11. Dict (empty {})
# =============================================================================
print("\n11. Empty dict ({}):")
m_start = m0()
dicts = [{} for _ in range(NUM_ITEMS)]
m_end = m0()
per_dict = (m_end - m_start) // NUM_ITEMS
print(f"  {NUM_ITEMS} empty dicts → {m_end - m_start} bytes total")
print(f"  ~{per_dict} bytes per dict")

del dicts
m0()

# =============================================================================
# 12. Final GC & Summary
# =============================================================================
print("\n--- Final GC ---")
gc.collect()
final_alloc = gc.mem_alloc()
final_free = gc.mem_free()
print(f"Final: Allocated = {final_alloc} B, Free = {final_free} B")