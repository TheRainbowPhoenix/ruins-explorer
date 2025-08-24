#!/usr/bin/env python3
import struct
import gint
import gc

def mem_used():
    gc.collect()
    return gc.mem_alloc()

def read_pak_tiles():
    HDR_FMT = '<4sHHII'
    ENT_FMT = '<32sBBHHHHHIIII'
    
    mem_start = mem_used()
    print(f"Memory before: {mem_start} bytes")
    
    with open('tiles.pak', 'rb') as f:
        # Read header
        magic, version, count, index_off, _ = struct.unpack(HDR_FMT, f.read(16))
        if magic != b'GIPK' or version != 1:
            raise ValueError('Bad PAK header')
        
        print(f"PAK: {count} tiles, index at {index_off}")
        
        # Read first 10 entries from index
        f.seek(index_off)
        tiles_to_draw = min(80, count)
        
        # Reusable buffers
        pal_buf = bytearray(1024)  # Assume max 512 colors * 2 bytes
        dat_buf = bytearray(32 * 32 * 2)  # 32x32 RGB565 tile
        
        x, y = 0, 0
        for i in range(tiles_to_draw):
            # Read entry
            raw = f.read(60)
            (name, profile, _r1, color_count, width, height, stride, _r2,
             pal_len, data_len, pal_off, data_off) = struct.unpack(ENT_FMT, raw)
            
            # Decode name
            z = name.find(b'\x00')
            tile_name = name[:z if z >= 0 else len(name)]
            
            # Resize buffers if needed
            if pal_len > len(pal_buf):
                print("Resize buffers pal", pal_len)
                pal_buf = bytearray(pal_len)
            if data_len > len(dat_buf):
                print("Resize buffers data", data_len)
                dat_buf = bytearray(data_len)
            
            # Save current position
            pos = f.tell()
            
            # Read palette
            f.seek(pal_off)
            f.readinto(memoryview(pal_buf)[:pal_len])
            
            # Read data
            f.seek(data_off)
            f.readinto(memoryview(dat_buf)[:data_len])
            
            # Create memoryviews for gint
            mv_pal = memoryview(pal_buf)[:pal_len]
            mv_dat = memoryview(dat_buf)[:data_len]
            
            # Create and draw image
            img = gint.image(profile, color_count, width, height, stride, mv_dat, mv_pal)
            gint.dimage(x, y, img)
            
            # Clean up image immediately
            del img
            
            # Update position for next tile
            x += 32
            if x >= 320:
                x = 0
                y += 32
            
            print(f"Drew tile {i}: {tile_name} ({width}x{height})")
            
            # Restore file position
            f.seek(pos)
    
    gint.dupdate()
    
    # Final cleanup
    del pal_buf, dat_buf
    gc.collect()
    
    mem_end = mem_used()
    print(f"Memory after: {mem_end} bytes")
    print(f"Memory used: {mem_end - mem_start} bytes")
    
    gint.getkey()

read_pak_tiles()