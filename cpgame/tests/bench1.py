import time
import gc

from .engine.geometry import Vec2


import time
import gc
from .engine.geometry import Vec2

def benchmark_vec2():
    vectors = []
    count = 0
    batch_size = 10000  # Process in batches to avoid immediate memory issues
    
    print("Starting Vec2 memory benchmark...")
    start_time = time.time()
    
    try:
        while True:
            # Create a batch of vectors
            batch = []
            for i in range(batch_size):
                v = Vec2(count + i, (count + i) * 2)
                batch.append(v)
            
            vectors.extend(batch)
            count += batch_size
            
            # Print progress every 50k vectors
            if count % 500 == 0:
                print(f"Created {count} vectors...")
                # Force garbage collection to get more accurate memory usage
                gc.collect()
            
            # Check if we're taking too long (optional safety break)
            if time.time() - start_time > 30:  # Stop after 30 seconds
                print("Stopping after 30 seconds...")
                break
                
    except MemoryError:
        print(f"MemoryError caught after creating approximately {count} vectors")
    except Exception as e:
        print(f"Exception caught: {type(e).__name__}: {e}")
        print(f"Managed to create approximately {count} vectors")
    
    end_time = time.time()
    print(f"Vec2 benchmark completed:")
    print(f"  - Time elapsed: {end_time - start_time:.4f} seconds")
    print(f"  - Vectors created: {count}")
    print(f"  - Rate: {count / (end_time - start_time):.0f} vectors/second" if end_time - start_time > 0 else "")
    
    # Clean up
    del vectors
    gc.collect()

def benchmark_vec2_operations():
    """Benchmark operations on a reasonable number of vectors"""
    print("\nStarting Vec2 operations benchmark...")
    vectors = []
    test_size = 50000  # More reasonable size
    
    start_time = time.time()
    
    try:
        # Create vectors
        creation_start = time.time()
        for i in range(test_size):
            v = Vec2(i, i * 2)
            vectors.append(v)
        creation_time = time.time() - creation_start
        print(f"Created {test_size} vectors in {creation_time:.4f} seconds")
        
        # Perform operations
        operations_start = time.time()
        for v in vectors:
            v2 = v + Vec2(1, 1)
            v3 = v2 * 2
            # Simple operations since Vec2 doesn't have clone
            _ = Vec2(v3.x, v3.y)  # Equivalent to clone
        
        operations_time = time.time() - operations_start
        total_time = time.time() - start_time
        
        print(f"Operations completed in {operations_time:.4f} seconds")
        print(f"Total time: {total_time:.4f} seconds")
        print(f"Overall rate: {test_size / total_time:.0f} vectors/second" if total_time > 0 else "")
        
    except MemoryError:
        print(f"MemoryError during operations with {len(vectors)} vectors")
    except Exception as e:
        print(f"Exception during operations: {type(e).__name__}: {e}")
    
    # Clean up
    del vectors
    gc.collect()


print("Running Vec2 benchmarks...")
benchmark_vec2()
benchmark_vec2_operations()
