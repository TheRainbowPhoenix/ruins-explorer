# tile_draw_binary.py
import sys, gc, gint, time
import struct

TILE_SIZE = 16

def mem_used():
    """Get current memory usage with forced garbage collection"""
    gc.collect()
    return gc.mem_alloc()

def timeit(func):
    """Time a function execution"""
    start = time.monotonic()
    result = func()
    end = time.monotonic()
    elapsed = end - start
    return result, elapsed

def _screen_size():
    try:
        return gint.DWIDTH, gint.DHEIGHT
    except Exception:
        return 320, 528

class BinaryImageLoader:
    """
    Efficient binary image loader that reuses memory buffers.
    Reads image data from .bin files instead of importing modules.
    """
    
    def __init__(self, max_buffer_size=64*1024):  # 64KB default buffer
        self.max_buffer_size = max_buffer_size
        self.image_buffer = None
        self.current_file = None
        self.current_filename = None
        
        # Image metadata (read from file header or assumed)
        self.image_width = 0
        self.image_height = 0
        self.bytes_per_pixel = 2  # Assuming 16-bit color
        
        print(f"BinaryImageLoader initialized with {max_buffer_size} byte buffer")
    
    def _ensure_buffer(self, required_size):
        """Ensure buffer exists and is large enough"""
        if required_size > self.max_buffer_size:
            # For very large images, we'll need to process in chunks
            if self.image_buffer is None or len(self.image_buffer) < self.max_buffer_size:
                print(f"Creating buffer: {self.max_buffer_size} bytes")
                self.image_buffer = bytearray(self.max_buffer_size)
        else:
            if self.image_buffer is None or len(self.image_buffer) < required_size:
                print(f"Resizing buffer to: {required_size} bytes")
                self.image_buffer = bytearray(required_size)
    
    def open_image_file(self, filename):
        """Open a binary image file"""
        if self.current_filename == filename and self.current_file:
            return  # Already open
        
        self.close_current_file()
        
        try:
            self.current_file = open(filename, 'rb')
            self.current_filename = filename
            
            # Read image dimensions from file header (first 8 bytes)
            # Format: width (4 bytes), height (4 bytes), then image data
            header = self.current_file.read(8)
            if len(header) >= 8:
                self.image_width, self.image_height = struct.unpack('<II', header)
                print(f"Opened {filename}: {self.image_width}x{self.image_height}")
            else:
                # Fallback: assume square tileset
                file_size = self.current_file.seek(0, 2)  # Seek to end
                self.current_file.seek(0)  # Reset
                
                # Estimate dimensions (assuming square image)
                pixels = file_size // self.bytes_per_pixel
                dimension = int(pixels ** 0.5)
                self.image_width = self.image_height = dimension
                print(f"Estimated dimensions for {filename}: {dimension}x{dimension}")
                
        except Exception as e:
            print(f"Error opening {filename}: {e}")
            self.close_current_file()
            raise
    
    def close_current_file(self):
        """Close current file and cleanup"""
        if self.current_file:
            self.current_file.close()
            self.current_file = None
            self.current_filename = None
    
    def read_tile_data(self, tile_x, tile_y, tile_size=TILE_SIZE):
        """
        Read a single tile's data from the current image file.
        Returns memoryview for zero-copy access.
        """
        if not self.current_file:
            raise RuntimeError("No image file open")
        
        tile_data_size = tile_size * tile_size * self.bytes_per_pixel
        self._ensure_buffer(tile_data_size)
        
        tiles_per_row = self.image_width // tile_size
        
        # Calculate file position for this tile
        tile_index = tile_y * tiles_per_row + tile_x
        
        # Read tile data row by row (tiles might not be contiguous in file)
        bytes_read = 0
        for row in range(tile_size):
            # Calculate position of this row in the source image
            src_y = tile_y * tile_size + row
            src_x = tile_x * tile_size
            
            # File offset for this row (assuming row-major order)
            row_offset = 8 + (src_y * self.image_width + src_x) * self.bytes_per_pixel
            
            # Seek to row position
            self.current_file.seek(row_offset)
            
            # Read one row of tile data
            row_size = tile_size * self.bytes_per_pixel
            row_start = bytes_read
            
            actual_read = self.current_file.readinto(
                memoryview(self.image_buffer)[row_start:row_start + row_size]
            )
            
            bytes_read += actual_read
            
            if actual_read != row_size:
                print(f"Warning: Expected {row_size} bytes, got {actual_read}")
                break
        
        return memoryview(self.image_buffer)[:bytes_read]
    
    def read_full_image_chunked(self, chunk_callback):
        """
        Read full image in chunks, calling callback for each chunk.
        Useful for very large images that don't fit in memory.
        """
        if not self.current_file:
            raise RuntimeError("No image file open")
        
        total_size = self.image_width * self.image_height * self.bytes_per_pixel
        chunk_size = self.max_buffer_size
        self._ensure_buffer(chunk_size)
        
        self.current_file.seek(8)  # Skip header
        bytes_processed = 0
        
        while bytes_processed < total_size:
            remaining = total_size - bytes_processed
            current_chunk_size = min(chunk_size, remaining)
            
            # Read chunk into buffer
            bytes_read = self.current_file.readinto(
                memoryview(self.image_buffer)[:current_chunk_size]
            )
            
            if bytes_read == 0:
                break
            
            # Process chunk
            chunk_data = memoryview(self.image_buffer)[:bytes_read]
            chunk_callback(chunk_data, bytes_processed)
            
            bytes_processed += bytes_read
            
            # Optional: force GC every few chunks
            if bytes_processed % (chunk_size * 4) == 0:
                gc.collect()
        
        return bytes_processed
    
    def cleanup(self):
        """Clean up all resources"""
        self.close_current_file()
        if self.image_buffer:
            self.image_buffer = None
        gc.collect()


def draw_tilemap_fullscreen_from_binary(filename, tilemap=None, x0=0, y0=0, tile_size=TILE_SIZE, blank_index=-1):
    """
    Draw a tilemap from a binary file (.bin) instead of importing a module.
    Uses memory-efficient streaming approach.
    """
    mem_before = mem_used()
    print(f"Starting tilemap draw from {filename}")
    print(f"Initial memory: {mem_before} bytes")
    
    loader = BinaryImageLoader()
    
    try:
        # Open the binary image file
        def load_and_setup():
            loader.open_image_file(filename)
            return loader.image_width, loader.image_height
        
        (img_width, img_height), load_time = timeit(load_and_setup)
        print(f"File loaded in {load_time:.4f}s")
        
        screen_w, screen_h = _screen_size()
        cols = screen_w // tile_size
        rows = screen_h // tile_size
        
        tiles_per_row = img_width // tile_size
        tiles_per_col = img_height // tile_size
        total_tiles = tiles_per_row * tiles_per_col
        
        print(f"Screen: {screen_w}x{screen_h} ({cols}x{rows} tiles)")
        print(f"Tileset: {tiles_per_row}x{tiles_per_col} tiles ({total_tiles} total)")
        
        dsubimage = gint.dsubimage
        dupdate = gint.dupdate
        
        tiles_drawn = 0
        mem_peak = mem_before
        
        if tilemap is None:
            # AUTO: generate indices on the fly
            idx = 0
            for ty in range(rows):
                dy = y0 + ty * tile_size
                row_start_time = time.monotonic()
                
                for tx in range(cols):
                    dx = x0 + tx * tile_size
                    t = idx % total_tiles
                    
                    if t != blank_index:
                        # Calculate tile position in tileset
                        tile_x = t % tiles_per_row
                        tile_y = t // tiles_per_row
                        
                        # Read tile data (this reuses the buffer)
                        tile_data = loader.read_tile_data(tile_x, tile_y, tile_size)
                        
                        # Convert to image and draw
                        # Note: You'll need to adapt this to your specific image format
                        # This is a placeholder for the actual drawing
                        sx = tile_x * tile_size
                        sy = tile_y * tile_size
                        
                        # If you have a way to create image from buffer:
                        # temp_img = create_image_from_buffer(tile_data, tile_size, tile_size)
                        # dsubimage(dx, dy, temp_img, 0, 0, tile_size, tile_size)
                        
                        tiles_drawn += 1
                    
                    idx += 1
                    
                    # Memory monitoring
                    if tiles_drawn % 50 == 0:  # Check every 50 tiles
                        current_mem = mem_used()
                        mem_peak = max(mem_peak, current_mem)
                
                # Update screen per row
                dupdate()
                
                row_time = time.monotonic() - row_start_time
                if ty % 5 == 0:  # Progress every 5 rows
                    current_mem = mem_used()
                    print(f"Row {ty}/{rows}: {row_time:.4f}s, {current_mem} bytes")
        
        else:
            # EXPLICIT: use provided tilemap
            for ty in range(min(rows, len(tilemap))):
                row = tilemap[ty]
                dy = y0 + ty * tile_size
                row_start_time = time.monotonic()
                
                for tx in range(min(cols, len(row))):
                    t = row[tx]
                    if t == blank_index:
                        continue
                    
                    t %= total_tiles
                    dx = x0 + tx * tile_size
                    
                    # Calculate tile position
                    tile_x = t % tiles_per_row
                    tile_y = t // tiles_per_row
                    
                    # Read and draw tile
                    tile_data = loader.read_tile_data(tile_x, tile_y, tile_size)
                    
                    # Drawing code here (adapted to your format)
                    tiles_drawn += 1
                    
                    if tiles_drawn % 50 == 0:
                        current_mem = mem_used()
                        mem_peak = max(mem_peak, current_mem)
                
                dupdate()
                
                row_time = time.monotonic() - row_start_time
                if ty % 5 == 0:
                    current_mem = mem_used()
                    print(f"Row {ty}/{rows}: {row_time:.4f}s, {current_mem} bytes")
    
    finally:
        # Cleanup
        cleanup_start = time.monotonic()
        loader.cleanup()
        cleanup_time = time.monotonic() - cleanup_start
        
        mem_after = mem_used()
        mem_used_total = mem_peak - mem_before
        mem_leaked = mem_after - mem_before
        
        print(f"\n--- Tilemap Drawing Complete ---")
        print(f"Tiles drawn: {tiles_drawn}")
        print(f"Peak memory used: {mem_used_total} bytes")
        print(f"Memory leaked: {mem_leaked} bytes")
        print(f"Cleanup time: {cleanup_time:.4f}s")


def draw_fullscreen_image_from_binary(filename, x=0, y=0):
    """
    Draw a fullscreen image from a binary file using chunked loading.
    """
    mem_before = mem_used()
    print(f"Drawing fullscreen image from {filename}")
    
    loader = BinaryImageLoader()
    
    try:
        loader.open_image_file(filename)
        
        # Process image in chunks
        def chunk_processor(chunk_data, offset):
            # Process each chunk of image data
            # This would convert the chunk to displayable format and draw it
            # Implementation depends on your graphics system
            pass
        
        def process_image():
            return loader.read_full_image_chunked(chunk_processor)
        
        bytes_processed, process_time = timeit(process_image)
        
        # Final screen update
        gint.dupdate()
        
        print(f"Processed {bytes_processed} bytes in {process_time:.4f}s")
        
    finally:
        loader.cleanup()
        mem_after = mem_used()
        print(f"Memory used: {mem_after - mem_before} bytes")


def create_test_binary_file(filename, width=128, height=128):
    """
    Create a test binary file for testing.
    Format: width(4), height(4), then pixel data
    """
    print(f"Creating test file: {filename}")
    
    with open(filename, 'wb') as f:
        # Write header
        f.write(struct.pack('<II', width, height))
        
        # Write test pattern data (16-bit color)
        for y in range(height):
            for x in range(width):
                # Create a simple pattern
                color = ((x % 32) << 11) | ((y % 64) << 5) | ((x + y) % 32)
                f.write(struct.pack('<H', color))
    
    print(f"Created {filename}: {width}x{height}")


# Test and example usage
def test_memory_and_performance():
    """Test the binary tile system with memory monitoring"""
    print("Testing binary tile drawing system...")
    
    # Create test files
    test_files = ['a_img.bin', 'b_img.bin', 'c_img.bin', 'd_img.bin']
    
    for i, filename in enumerate(test_files):
        size = 64 + i * 32  # Different sizes for testing
        create_test_binary_file(filename, size, size)
    
    print("\n--- Testing Tile Drawing ---")
    
    total_mem_start = mem_used()
    
    # Test drawing multiple images (like your original loop)
    for name in ['a_img.bin', 'b_img.bin', 'c_img.bin', 'd_img.bin'] * 2:
        print(f"\n=== Drawing {name} ===")
        
        def draw_test():
            draw_tilemap_fullscreen_from_binary(name)
        
        _, draw_time = timeit(draw_test)
        print(f"Total draw time: {draw_time:.4f}s")
        
        # Optional: pause between images
        # gint.getkey()
    
    total_mem_end = mem_used()
    print(f"\n=== Final Results ===")
    print(f"Total memory change: {total_mem_end - total_mem_start} bytes")
    
    return total_mem_end - total_mem_start


if __name__ == "__main__":
    # Run the test
    test_memory_and_performance()
    
    print("\nTest complete. Press key to continue...")
    try:
        gint.getkey()
    except:
        pass