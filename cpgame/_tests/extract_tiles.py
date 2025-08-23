#!/usr/bin/env python3
import struct
import sys
import os
import gint

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
            img = gint.image(
                e['profile'],
                e['color_count'],
                e['width'],
                e['height'],
                e['stride'],
                data,
                pal
            )
            
            # Draw to screen
            gint.dimage(dx, dy, img)
            gint.dupdate()
            
            # Increment position
            dx += tile_width
            if dx >= max_width:
                dx = 0
                dy += tile_height
            
            # Wait for keypress between tiles (optional)
            # gint.getkey()
            
            # Clean up
            del img

        index_off = f.tell()
        for b in blobs:
            f.write(_ENT.pack(*b))

        # patch header with index offset
        f.seek(8)
        f.write(struct.pack('<I', index_off))

def extract_tiles_from_a_img():
    """Extract 32x32 tiles from the existing chessboard.py format"""
    
    # Import the existing chessboard module
    try:
        import chessboard
    except ImportError:
        print("Error: Cannot import chessboard.py. Make sure it's in the same directory.")
        return []
    
    # Get the image data from chessboard
    img_obj = chessboard.image
    
    # Extract image properties
    profile = img_obj.profile
    color_count = img_obj.color_count
    width = img_obj.width
    height = img_obj.height
    stride = img_obj.stride
    data = img_obj.data
    palette = img_obj.palette
    
    print(f"Original image: {width}x{height}, profile={profile}, stride={stride}")
    print(f"Data length: {len(data)}, Palette length: {len(palette)}")
    
    # Validate data size
    expected_data_size = stride * height
    if len(data) != expected_data_size:
        print(f"Warning: Data size mismatch. Expected {expected_data_size}, got {len(data)}")
    
    # Calculate number of tiles
    tile_width, tile_height = 32, 32
    cols = width // tile_width
    rows = height // tile_height
    total_tiles = cols * rows
    
    print(f"Will extract {total_tiles} tiles ({cols}x{rows})")
    
    entries = []
    
    # Extract each tile
    for row in range(rows):
        for col in range(cols):
            tile_idx = row * cols + col
            
            # Calculate tile boundaries
            x_start = col * tile_width
            y_start = row * tile_height
            
            # Create tile data - for RGB565, each pixel is 2 bytes
            tile_stride = tile_width * 2
            tile_data = bytearray(tile_stride * tile_height)
            
            # Copy pixel data from original image to tile
            for y in range(tile_height):
                # Calculate source row start
                src_row_start = (y_start + y) * stride + (x_start)
                # Calculate destination row start  
                dst_row_start = y * tile_stride
                
                # Copy entire row of tile data at once
                row_bytes = tile_width * 2
                if src_row_start + row_bytes <= len(data):
                    tile_data[dst_row_start:dst_row_start + row_bytes] = data[src_row_start:src_row_start + row_bytes]
            
            # Create entry for this tile
            entry = {
                'name': f"tile_{tile_idx:03d}",
                'profile': profile,
                'color_count': color_count,
                'width': tile_width,
                'height': tile_height,
                'stride': tile_stride,
                'palette': palette,
                'data': tile_data
            }
            
            entries.append(entry)
            print(f"Created tile {tile_idx}: {tile_width}x{tile_height}")
    
    return entries

def main():
    print("Extracting tiles from a_img.py...")
    
    entries = extract_tiles_from_a_img()
    
    if not entries:
        print("No tiles extracted!")
        return
    
    # Write PAK file
    pak_file = 'tiles.pak'
    pack(pak_file, entries)
    print(f"Created PAK file: {pak_file} with {len(entries)} tiles")
    
    # Show file info
    stat = os.stat(pak_file)
    print(f"PAK file size: {stat.st_size} bytes")

    gint.getkey()

if __name__ == "__main__":
    main()