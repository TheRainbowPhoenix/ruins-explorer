#!/usr/bin/env python3
import gint
import struct
import sys
import os

# ---- PAK layout (same as before) ----
_HDR = struct.Struct('<4sHHII')
_ENT = struct.Struct('<32sBBHHHHHIIII')

def pack(out_path, entries):
    with open(out_path, 'wb') as f:
        f.write(_HDR.pack(b'GIPK', 1, len(entries), 0, 0))  # placeholder (index_off=0)

        blobs = []
        dx = 0
        dy = 0
        tile_width = 32
        tile_height = 32
        max_width = 320  # Assuming screen width
        
        for e in entries:
            name = e['name'].encode('ascii')[:31]
            name = name + b'\x00' * (32 - len(name))
            pal = e['palette']
            data = e['data']
            pal_off = f.tell()
            f.write(pal)
            data_off = f.tell()
            f.write(data)
            blobs.append((
                name,
                e['profile'],
                e.get('reserved', 0),
                
                e['color_count'],
                e['width'],
                e['height'],
                e['stride'],
                0,
                len(pal), len(data), pal_off, data_off
                # <32s BB HHHHH IIII
            ))
            
            # Draw to screen
            try:
                img = gint.image(
                    e['profile'],
                    e['color_count'],
                    e['width'],
                    e['height'],
                    e['stride'],
                    data,
                    pal
                )
                
                gint.dimage(dx, dy, img)
                gint.dupdate()

                print(f"{e['name']} ", {
                    "profile":  e['profile'],
                    "color_count": e['color_count'],
                    "width": e['width'],
                    "height": e['height'],
                    "stride": e['stride'],
                })

                # hex_str = ' '.join([f'{b:02x}' for b in pal])
                # hex_dat = ' '.join([f'{b:02x}' for b in data])
                # print(f"{e['name']} pal: [ {hex_str} ]")
                # print(f"{e['name']} dat: [ {hex_dat} ]")
                
                # Increment position
                dx += tile_width
                if dx >= max_width:
                    dx = 0
                    dy += tile_height
                
                # Wait for keypress between tiles (optional)
                # gint.getkey()
                
                # Clean up
                del img
            except:
                pass

            

        index_off = f.tell()
        for b in blobs:
            f.write(_ENT.pack(*b))

        # patch header with index offset
        f.seek(8)
        f.write(struct.pack('<I', index_off))

def extract_tiles_from_module(module_name, prefix):
    """Extract 32x32 tiles from a module containing face images"""
    
    try:
        mod = __import__(module_name, None, None, ('image',))
    except ImportError:
        print(f"Error: Cannot import {module_name}. Make sure it's in the same directory.")
        return []
    
    entries = []
    tile_idx = 0
    
    img_obj = mod.image

    # Extract image properties
    profile = img_obj.profile
    color_count = img_obj.color_count
    width = img_obj.width
    height = img_obj.height
    stride = img_obj.stride
    data = img_obj.data
    palette = img_obj.palette
    
    print(f"Processing {module_name}: {width}x{height}, profile={profile}, stride={stride}")
    print(f"Data length: {len(data)}, Palette length: {len(palette)}")
    
    # Validate data size
    expected_data_size = stride * height
    if len(data) != expected_data_size:
        print(f"Warning: Data size mismatch. Expected {expected_data_size}, got {len(data)}")
    
    # Calculate number of tiles (assuming 32x32 tiles)
    tile_width, tile_height = 32, 32
    cols = width // tile_width
    rows = height // tile_height
    total_tiles = cols * rows
    
    print(f"Will extract {total_tiles} tiles ({cols}x{rows}) from {module_name}")
    
    entries = []
    
    # Extract each tile
    for row in range(rows):
        for col in range(cols):
            tile_idx_local = row * cols + col
            
            # Calculate tile boundaries
            x_start = col * tile_width
            y_start = row * tile_height
            
            # Create tile data - for RGB565, each pixel is 2 bytes
            tile_stride = tile_width * 2
            tile_data = bytearray(tile_stride * tile_height)
            
            # Copy pixel data from original image to tile
            for y in range(tile_height):
                # Calculate source row start (for RGB565)
                src_row_start = (y_start + y) * stride + (x_start)
                # Calculate destination row start  
                dst_row_start = y * tile_stride
                
                # Copy entire row of tile data at once
                row_bytes = tile_width * 2
                if src_row_start + tile_width <= len(data):
                    tile_data[dst_row_start:dst_row_start + row_bytes] = data[src_row_start:src_row_start + row_bytes]
            
            # Create entry for this tile
            entry = {
                'name': f"{prefix}_{tile_idx_local:03d}",
                'profile': profile,
                'color_count': color_count,
                'width': tile_width,
                'height': tile_height,
                'stride': tile_stride,
                'palette': palette,
                'data': tile_data
            }
            
            entries.append(entry)
            print(f"Created tile {entry['name']}: {tile_width}x{tile_height}")
            tile_idx += 1
    
    return entries

def extract_tiles_from_multiple_modules(modules_and_prefixes):
    """Extract tiles from multiple modules with different prefixes"""
    all_entries = []
    
    for module_name, prefix in modules_and_prefixes:
        print(f"\n--- Extracting from {module_name} with prefix '{prefix}' ---")
        entries = extract_tiles_from_module(module_name, prefix)
        all_entries.extend(entries)
        print(f"Extracted {len(entries)} entries from {module_name}")
    
    return all_entries

def main():
    print("Extracting face tiles...")
    
    # Define modules and prefixes to extract from
    modules_and_prefixes = [
        ('enemies.cabbit', 'cabbit'),
        ('enemies.vorpal', 'vorpal'),
        # ('faces.holo11', 'holo11'),
        # ('mini_faces.bg1', 'bg1'),
        # ('mini_faces.bg2', 'bg2'),
        # ('mini_faces.bg3', 'bg3'),
        # ('mini_faces.bg4', 'bg4'),
        # Add more modules here if needed
        # ('other_faces', 'other_'),
    ]
    
    entries = extract_tiles_from_multiple_modules(modules_and_prefixes)
    
    if not entries:
        print("No tiles extracted!")
        return
    
    # Write PAK file
    pak_file = 'enemies.pak'
    pack(pak_file, entries)
    print(f"\nCreated PAK file: {pak_file} with {len(entries)} tiles")
    
    # Show file info
    try:
        stat = os.stat(pak_file)
        print(f"PAK file size: {stat.st_size} bytes")
    except:
        pass

    try:
        gint.getkey()
    except:
        pass

if __name__ == "__main__":
    main()