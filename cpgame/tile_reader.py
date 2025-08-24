import struct
import gint
import gc

# ---- structs (little-endian)
HDR_FMT = '<4sHHII'                # magic, version, count, index_off, reserved
HDR_SIZE = 16 # struct.calcsize(HDR_FMT)

ENT_FMT = '<32sBBHHHHHIIII'        # name[32], profile,u8,res,u8,cc,u16,w,h,stride,res,u16, plen,u32,dlen,u32, poff,u32, doff,u32
ENT_SIZE = 60 # struct.calcsize(ENT_FMT)


# _HDR = struct.Struct('<4sHHII')           # magic, version, count, index_off, reserved
# _ENT = struct.Struct('<32sBBHHHHHIIII')    # see layout above

class PakReader:
    def __init__(self, path):
        self.f = open(path, 'rb')
        self._index = None
        self._count = 0
        self._load_header()

        # Reusable buffers (set on first load)
        self._data_buf = None
        self._pal_buf = None

    def close(self):
        try:
            self.f.close()
        except:  # noqa: E722 (keep tiny)
            pass

    def _load_header(self):
        f = self.f
        f.seek(0)
        magic, version, count, index_off, _ = struct.unpack(HDR_FMT, f.read(HDR_SIZE)) # _HDR.unpack(f.read(_HDR.size))
        if magic != b'GIPK' or version != 1:
            raise ValueError('Bad PAK header')
        self._count = count
        # Lazy-load index on demand
        self._index_off = index_off

    def _load_index(self):
        if self._index is not None:
            return
        f = self.f
        f.seek(self._index_off)
        idx = []
        for _ in range(self._count):
            # raw = f.read(_ENT.size)
            (name, _r0, _r1, color_count, width, height, stride, _r2,
             pal_len, data_len, pal_off, data_off) = struct.unpack(ENT_FMT, f.read(ENT_SIZE))
            # decode zero-terminated
            z = name.find(b'\x00')
            key = name[:z if z >= 0 else len(name)].decode('ascii')
            idx.append({
                'name': key,
                'color_count': color_count,
                'width': width,
                'height': height,
                'stride': stride,
                'palette_len': pal_len,
                'data_len': data_len,
                'palette_off': pal_off,
                'data_off': data_off,
                'profile': _r0,  # we packed 'profile' into that 1-byte slot
            })
        self._index = idx

    def find(self, name):
        self._load_index()
        # linear scan keeps memory tiny; optionally keep dict if you have many entries
        for e in self._index:
            if e['name'] == name:
                return e
        return None

    def load_into_buffers(self, entry, want_reuse=True):
        """Read palette+pixels straight into reusable bytearrays."""
        f = self.f

        pal_len = entry['palette_len']
        data_len = entry['data_len']

        # (Re)allocate once, then keep
        if (not want_reuse) or (self._pal_buf is None) or (len(self._pal_buf) < pal_len):
            self._pal_buf = bytearray(pal_len)
        if (not want_reuse) or (self._data_buf is None) or (len(self._data_buf) < data_len):
            self._data_buf = bytearray(data_len)

        mv_pal = memoryview(self._pal_buf)[:pal_len]
        mv_dat = memoryview(self._data_buf)[:data_len]

        # Read without extra copies
        f.seek(entry['palette_off'])
        f.readinto(mv_pal)
        f.seek(entry['data_off'])
        f.readinto(mv_dat)

        gc.collect()
        return mv_pal, mv_dat  # memoryviews backed by reusable buffers

    def draw_tilemap(self, x0=0, y0=0, tile_width=32, tile_height=32):
        """Draw all tiles from the PAK file as a grid"""
        if self._index is None:
            self._load_index()
        
        # Calculate grid dimensions based on screen size
        # Assuming standard 320x528 screen
        cols = 10  # 320/32 = 10
        rows = 16  # 528/32 = 16
        
        print(f"Drawing {len(self._index)} tiles in {cols}x{rows} grid")
        
        # Draw each tile
        tile_idx = 0
        for row in range(rows):
            for col in range(cols):
                if tile_idx >= len(self._index):
                    break
                    
                entry = self._index[tile_idx]
                
                # Calculate position
                dx = x0 + col * tile_width
                dy = y0 + row * tile_height
                
                # Load and draw tile with fresh buffers
                try:
                    # Use the new method that creates fresh buffers
                    self._draw_tile_with_fresh_buffers(entry, dx, dy)
                    
                    tile_idx += 1
                    
                except Exception as e:
                    print(f"Error drawing tile {entry['name']}: {e}")
                    tile_idx += 1
                    
                # Periodic garbage collection
                if tile_idx % 5 == 0:
                    gc.collect()
            gint.dupdate()

    def _draw_tile_with_fresh_buffers(self, entry, x, y):
        """Internal method to draw a tile with fresh buffers"""
        # Read palette directly into a fresh buffer
        pal_buf = bytearray(entry['palette_len'])
        self.f.seek(entry['palette_off'])
        self.f.readinto(pal_buf)
        mv_pal = memoryview(pal_buf)
        
        # Read data directly into a fresh buffer
        data_buf = bytearray(entry['data_len'])
        self.f.seek(entry['data_off'])
        self.f.readinto(data_buf)
        mv_dat = memoryview(data_buf)
        
        # Create image object
        img = gint.image(
            entry['profile'],
            entry['color_count'],
            entry['width'],
            entry['height'],
            entry['stride'],
            mv_dat, # memoryview
            mv_pal # memoryview
        )
        
        # Draw to screen
        gint.dimage(x, y, img)
        
        # Clean up temporary objects
        del img, pal_buf, data_buf
        gc.collect()

    def draw_single_tile(self, name, x, y, gint):
        """Load -> construct gint.image -> draw -> release the *image* object."""
        entry = self.find(name)
        if not entry:
            raise KeyError(name)

        # Read palette directly into a fresh buffer
        pal_buf = bytearray(entry['palette_len'])
        self.f.seek(entry['palette_off'])
        self.f.readinto(pal_buf)
        mv_pal = memoryview(pal_buf)
        
        # Read data directly into a fresh buffer
        data_buf = bytearray(entry['data_len'])
        self.f.seek(entry['data_off'])
        self.f.readinto(data_buf)
        mv_dat = memoryview(data_buf)

        # Build the transient image object
        img = gint.image(
            entry['profile'],
            entry['color_count'],
            entry['width'],
            entry['height'],
            entry['stride'],
            mv_dat,
            mv_pal
        )

        # Draw to screen
        gint.dimage(x, y, img)

        # Drop the temporary Python object
        del img, pal_buf, data_buf
        gc.collect()

    def draw_with_new_palette(self, name, x, y, gint):
        """Draw a tile with fresh palette loading (no buffer reuse) - EXPOSED METHOD"""
        entry = self.find(name)
        if not entry:
            raise KeyError(name)

        # Read palette directly into a fresh buffer
        pal_buf = bytearray(entry['palette_len'])
        self.f.seek(entry['palette_off'])
        self.f.readinto(pal_buf)
        mv_pal = memoryview(pal_buf)
        
        # Read data directly into a fresh buffer
        data_buf = bytearray(entry['data_len'])
        self.f.seek(entry['data_off'])
        self.f.readinto(data_buf)
        mv_dat = memoryview(data_buf)

        # Build the transient image object
        img = gint.image(
            entry['profile'],
            entry['color_count'],
            entry['width'],
            entry['height'],
            entry['stride'],
            mv_dat,
            mv_pal
        )

        # Draw to screen
        gint.dimage(x, y, img)

        # Clean up
        del img, pal_buf, data_buf
        gc.collect()

# Example usage
def test_memory():
    """Test memory usage"""
    def mem_used():
        gc.collect()
        return gc.mem_alloc()
    
    print("Memory test:")
    print(f"Initial: {mem_used()} bytes")
    
    try:
        pak = PakReader('tiles.pak')
        print(f"After PAK load: {mem_used()} bytes")
        
        # Simulate drawing tiles (uncomment when running on device)
        pak.draw_tilemap(0, 0, 32, 32)
        
        print(f"Before close: {mem_used()} bytes")
        pak.close()
        print(f"After close: {mem_used()} bytes")

        gint.getkey()
        
    except Exception as e:
        print(f"Error: {e}")
        print(f"Memory at error: {mem_used()} bytes")
    finally:
        if pak:
            pak.close()

test_memory()