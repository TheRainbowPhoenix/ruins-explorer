import gint
import gc
import time

def mem_used():
    gc.collect()
    return gc.mem_alloc()

def test_memoryview_usage():
    print("Testing memoryview usage...")
    
    # Test 1: Basic memoryview creation and usage
    print("\n--- Test 1: Basic memoryview ---")
    mem_before = mem_used()
    
    # Create a large bytearray
    ba = bytearray(10000)  # 10KB array
    mem_after = mem_used()
    print(f"Bytearray creation: {mem_after - mem_before} bytes")
    
    # Create memoryview
    mem_before = mem_used()
    mv = memoryview(ba)
    mem_after = mem_used()
    print(f"Memoryview creation: {mem_after - mem_before} bytes")

    # Test 3: Memoryview slicing
    print("\n--- Test 3: Memoryview slicing ---")
    mem_before = mem_used()
    
    # Create a larger buffer and slice it
    large_buffer = bytearray(20000)
    large_mv = memoryview(large_buffer)
    
    # Slice it multiple times
    slices = []
    for i in range(10):
        slice_mv = large_mv[i*1000:(i+1)*1000]
        slices.append(slice_mv)
        # print(f"Slice {i}: {len(slice_mv)} bytes")
    
    mem_after = mem_used()
    print(f"Creating 10 slices: {mem_after - mem_before} bytes")
    
    # Test 4: Realistic tile reading scenario
    print("\n--- Test 4: Tile reading simulation ---")
    
    # Simulate reading from PAK file
    pak_file_size = 50000  # 50KB PAK file
    block_size = 1024      # 1KB blocks
    
    # Create a mock PAK file
    with open("tiles.pak", "wb") as f:
        f.write(b"B" * pak_file_size)
    
    mem_before = mem_used()
    
    # Create reusable buffer for reading
    read_buffer = bytearray(block_size)
    read_mv = memoryview(read_buffer)
    
    # Simulate reading 10 rounds of 1024 bytes
    with open("tiles.pak", "rb") as f:
        for round_num in range(100):
            bytes_read = f.readinto(read_mv)
            if bytes_read == 0:
                break
            
            # Process the block (simulated)
            # This is where you'd parse the PAK format and extract tiles
            processed_block = read_mv[:bytes_read]
            
            # Simulate processing
            if round_num % 2 == 0:
                # Do something with the data
                pass
            
            # print(f"Round {round_num}: {bytes_read} bytes processed")
    
    mem_after = mem_used()
    print(f"Reading 100 blocks (1024 bytes each): {mem_after - mem_before} bytes")

test_memoryview_usage()