import time
import gc
from .engine.geometry import Vector2

def benchmark_vector2():
    vectors = []
    count = 0
    batch_size = 10000  # Process in batches to avoid immediate memory issues
    
    print("Starting Vector2 memory benchmark...")
    start_time = time.time()
    
    try:
        while True:
            # Create a batch of vectors
            batch = []
            for i in range(batch_size):
                v = Vector2(count + i, (count + i) * 2)
                batch.append(v)
            
            vectors.extend(batch)
            count += batch_size
            
            # Print progress every 500 vectors (smaller number for Vector2 since it's heavier)
            if count % 500 == 0:
                print(f"Created {count} Vector2 objects...")
                # Force garbage collection to get more accurate memory usage
                gc.collect()
            
            # Check if we're taking too long (optional safety break)
            if time.time() - start_time > 30:  # Stop after 30 seconds
                print("Stopping after 30 seconds...")
                break
                
    except MemoryError:
        print(f"MemoryError caught after creating approximately {count} Vector2 objects")
    except Exception as e:
        print(f"Exception caught: {type(e).__name__}: {e}")
        print(f"Managed to create approximately {count} Vector2 objects")
    
    end_time = time.time()
    print(f"Vector2 benchmark completed:")
    print(f"  - Time elapsed: {end_time - start_time:.4f} seconds")
    print(f"  - Vector2 objects created: {count}")
    print(f"  - Rate: {count / (end_time - start_time):.0f} objects/second" if end_time - start_time > 0 else "")
    
    # Clean up
    del vectors
    gc.collect()

def benchmark_vector2_operations():
    """Benchmark operations on a reasonable number of Vector2 objects"""
    print("\nStarting Vector2 operations benchmark...")
    vectors = []
    test_size = 10000  # Smaller size due to heavier Vector2 operations
    
    start_time = time.time()
    
    try:
        # Create vectors
        creation_start = time.time()
        for i in range(test_size):
            v = Vector2(i, i * 2)
            vectors.append(v)
        creation_time = time.time() - creation_start
        print(f"Created {test_size} Vector2 objects in {creation_time:.4f} seconds")
        
        # Perform operations
        operations_start = time.time()
        for v in vectors:
            v.add(Vector2(1, 1))
            v.multiply(Vector2(2, 2))
            v.normalize()
            v.length()
            v.clone()
        
        operations_time = time.time() - operations_start
        total_time = time.time() - start_time
        
        print(f"Operations completed in {operations_time:.4f} seconds")
        print(f"Total time: {total_time:.4f} seconds")
        print(f"Overall rate: {test_size / total_time:.0f} objects/second" if total_time > 0 else "")
        
    except MemoryError:
        print(f"MemoryError during operations with {len(vectors)} Vector2 objects")
    except Exception as e:
        print(f"Exception during operations: {type(e).__name__}: {e}")
    
    # Clean up
    del vectors
    gc.collect()

print("Running Vector2 benchmarks...")
benchmark_vector2()
benchmark_vector2_operations()