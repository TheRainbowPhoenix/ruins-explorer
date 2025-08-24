#!/usr/bin/env python3
import gint
import struct
import gc

def mem_used():
    gc.collect()
    return gc.mem_alloc()

def list_pak_contents():
    HDR_FMT = '<4sHHII'
    ENT_FMT = '<32sBBHHHHHIIII'
    
    mem_start = mem_used()
    print(f"Memory before: {mem_start} bytes")
    

    with open('tiles.pak', 'rb') as f:
        # Read header
        magic, version, count, index_off, _ = struct.unpack(HDR_FMT, f.read(16))
        if magic != b'GIPK' or version != 1:
            raise ValueError('Bad PAK header')
        
        print(f"PAK Header:")
        print(f"  Magic: {magic}")
        print(f"  Version: {version}")
        print(f"  Count: {count}")
        print(f"  Index offset: {index_off}")
        print(f"  Reserved: {_}")
        
        # Read all entries from index
        f.seek(index_off)
        print(f.tell())
        print(f"\nListing {count} entries:")
        print("-" * 80)
        print(f"{'#':<3} {'Name':<20} {'Profile':<8} {'Size':<12} {'Palette':<15} {'Data':<15}")
        print("-" * 80)
        
        for i in range(min(count, 10)):
            # Read entry
            raw = f.read(60)
            if len(raw) < 60:
                print(f"Error: Could not read entry {i}")
                break

            hex_str = ' '.join([f'{b:02x}' for b in raw])
            print(f"[ {hex_str} ]")
                
            (name, profile, _r1, color_count, width, height, stride, _r2,
                pal_len, data_len, pal_off, data_off) = struct.unpack(ENT_FMT, raw)
            
            # Decode name
            z = name.find(b'\x00')
            tile_name = name[:z if z >= 0 else len(name)]
            
            # Print entry info
            size_str = f"{width}x{height}"
            pal_str = f"{pal_len}@{pal_off}"
            dat_str = f"{data_len}@{data_off}"
            
            print(f"{i:<3} {tile_name:<20} {profile:<8} {size_str:<12} {pal_str:<15} {dat_str:<15}")
            
            # Validate offsets
            if pal_off < 16 or data_off < 16:
                print(f"  WARNING: Invalid offset for entry {i}")
            
            # Check if this is one of the first few entries we want to examine
            if i < 5:  # Show details for first 5 entries
                print(f"    Details: {color_count} colors, stride={stride}")
        
        print("-" * 80)
        print(f"Total entries listed: {count}")
        
        # Try to read a small portion of first entry to test file integrity
        if count > 0:
            print(f"\nTesting first entry integrity...")
            f.seek(index_off)
            raw = f.read(60)
            (name, profile, _r1, color_count, width, height, stride, _r2,
                pal_len, data_len, pal_off, data_off) = struct.unpack(ENT_FMT, raw)
            
            # Decode name
            z = name.find(b'\x00')
            tile_name = name[:z if z >= 0 else len(name)].decode('ascii', errors='replace')
            
            print(f"First entry: {tile_name}")
            print(f"  Palette: {pal_len} bytes at offset {pal_off}")
            print(f"  Data: {data_len} bytes at offset {data_off}")
            
            # Try to seek to palette
            try:
                f.seek(pal_off)
                test_data = f.read(min(16, pal_len))
                print(f"  Palette test read: {len(test_data)} bytes")
            except Exception as e:
                print(f"  Palette read error: {e}")
            
            # Try to seek to data
            try:
                f.seek(data_off)
                test_data = f.read(min(16, data_len))
                print(f"  Data test read: {len(test_data)} bytes")
            except Exception as e:
                print(f"  Data read error: {e}")
    

    
    mem_end = mem_used()
    print(f"\nMemory after: {mem_end} bytes")
    print(f"Memory used: {mem_end - mem_start} bytes")

# Also create a simple file info function

print("PAK File Content Lister")
print("=" * 48)
list_pak_contents()