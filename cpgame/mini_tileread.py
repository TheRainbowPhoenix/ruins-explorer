import gint
import gc
import struct
import time

# ---- structs (little-endian)
HDR_FMT = '<4sHHII'                # magic, version, count, index_off, reserved
HDR_SIZE = 16 # struct.calcsize(HDR_FMT)

ENT_FMT = '<32sBBHHHHHIIII'        # name[32], profile,u8,res,u8,cc,u16,w,h,stride,res,u16, plen,u32,dlen,u32, poff,u32, doff,u32
ENT_SIZE = 60 # struct.calcsize(ENT_FMT)

def mem_used():
    gc.collect()
    return gc.mem_alloc()

def test_pak_reading_and_drawing():
    # Now test reading and drawing
    print("\n--- Starting PAK reading and drawing test ---")
    
    # Memory measurement before
    mem_before = mem_used()
    print(f"Memory before reading PAK: {mem_before} bytes")
    
    with open("tiles.pak", "rb") as f:
        # Read header
        f.seek(0)
        magic, version, count, index_off, _ = struct.unpack(HDR_FMT, f.read(HDR_SIZE))
        if magic != b'GIPK' or version != 1:
            raise ValueError('Bad PAK header')
        
        print(f"PAK Header: {count} entries, index at {index_off}")
        
        # Read index entries
        f.seek(index_off)
        entries = []
        for i in range(min(40, count)):  # Read first 10 entries
            raw_entry = f.read(ENT_SIZE)
            (name, profile, reserved0, color_count, width, height, stride, reserved1,
                pal_len, data_len, pal_off, data_off) = struct.unpack(ENT_FMT, raw_entry)
            
            # decode zero-terminated
            z = name.find(b'\x00')
            key = name[:z if z >= 0 else len(name)].decode('ascii')
            
            entry = {
                'name': key,
                'color_count': color_count,
                'width': width,
                'height': height,
                'stride': stride,
                'palette_len': pal_len,
                'data_len': data_len,
                'palette_off': pal_off,
                'data_off': data_off,
                'profile': profile,
            }
            entries.append(entry)
            print(f"Entry {i}: {key} ({width}x{height})")
        
        # Memory measurement after reading header/index
        mem_after_header = mem_used()
        print(f"Memory after reading header/index: {mem_after_header} bytes (+{mem_after_header - mem_before})")
        
        # Create reusable buffers
        data_buffer = bytearray(1024)  # Large enough for any tile data
        pal_buffer = bytearray(1024)   # Large enough for any palette
        
        data_mv = memoryview(data_buffer)
        pal_mv = memoryview(pal_buffer)
        
        # Draw first 10 tiles
        print("\nDrawing first 10 tiles...")
        for i, entry in enumerate(entries):
            print(f"Drawing tile {i}: {entry['name']}")
            
            # Seek to palette and read
            f.seek(entry['palette_off'])
            pal_len = entry['palette_len']
            if pal_len <= len(pal_buffer):
                f.readinto(pal_mv[:pal_len])
            
            # Seek to data and read
            f.seek(entry['data_off'])
            data_len = entry['data_len']
            if data_len <= len(data_buffer):
                f.readinto(data_mv[:data_len])
            
            # Create image object with memoryviews
            img = gint.image(
                entry['profile'],
                entry['color_count'],
                entry['width'],
                entry['height'],
                entry['stride'],
                data_mv,  # memoryview of data
                pal_mv[:pal_len]     # memoryview of palette
            )
            
            # Draw to screen (mock)
            gint.dimage(0, i * 32, img)
            gint.dupdate()
            
            # Clean up temporary objects
            del img
            
            # Periodic garbage collection
            if i % 2 == 0:
                gc.collect()
        
        # Memory measurement after drawing
        mem_after_draw = mem_used()
        print(f"Memory after drawing 10 tiles: {mem_after_draw} bytes (+{mem_after_draw - mem_before})")
        
        gint.getkey()

        # Cleanup
        del data_buffer, pal_buffer, data_mv, pal_mv
        gc.collect()
        
        mem_final = mem_used()
        print(f"Memory after cleanup: {mem_final} bytes (+{mem_final - mem_before})")
        


    
    print("\n--- Test completed ---")
    print(f"Total memory increase during test: {mem_final - mem_before} bytes")

test_pak_reading_and_drawing()