# cpgame/modules/pakloader.py
# A dynamic PAK file loader for loading and drawing image tiles on the fly.

import sys
import gc
import struct

try:
    import gint
except:
    pass

try:
    from typing import Optional, Any, Dict, List
except:
    pass

def mem_used():
    gc.collect()
    return gc.mem_alloc()

# ---- PAK Format structs (little-endian)
HDR_FMT = '<4sHHII'                # magic, version, count, index_off, reserved
ENT_FMT = '<32sBBHHHHHIIII'        # name[32], profile,u8,res,u8,cc,u16,w,h,stride,res,u16, plen,u32,dlen,u32, poff,u32, doff,u32
HDR_SIZE = 16
ENT_SIZE = 60

class PakEntry:
    """Represents a single entry in a PAK file"""
    def __init__(self, name, profile, color_count, width, height, stride, 
                 palette_len, data_len, palette_off, data_off):
        self.name = name
        self.profile = profile
        self.color_count = color_count
        self.width = width
        self.height = height
        self.stride = stride
        self.palette_len = palette_len
        self.data_len = data_len
        self.palette_off = palette_off
        self.data_off = data_off

class PakFile:
    """Represents an open PAK file with lazy-loaded index"""
    def __init__(self, filepath):
        self.filepath = filepath
        self._file = None
        self._entries = None
        self._count = 0
        self._index_off = 0
        self._pal_buf = None
        self._dat_buf = None
        self._open()

    def _open(self):
        """Open the PAK file and read header"""
        try:
            self._file = open(self.filepath, 'rb')
            # Read header
            magic, version, count, index_off, _ = struct.unpack(HDR_FMT, self._file.read(HDR_SIZE))
            if magic != b'GIPK' or version != 1:
                raise ValueError('Bad PAK header in {}'.format(self.filepath))
            self._count = count
            self._index_off = index_off
        except Exception as e:
            print("Error opening PAK file {}: {}".format(self.filepath, e))
            # Ensure file is closed even if header reading fails
            if self._file:
                try:
                    self._file.close()
                except:
                    pass
                self._file = None
            raise

    def _load_index(self):
        """Lazy-load the index entries"""
        if self._entries is not None:
            return
            
        self._file.seek(self._index_off)
        self._entries = []
        
        for _ in range(self._count):
            raw = self._file.read(ENT_SIZE)
            if len(raw) < ENT_SIZE:
                break
                
            (name, profile, _r1, color_count, width, height, stride, _r2,
             pal_len, data_len, pal_off, data_off) = struct.unpack(ENT_FMT, raw)
            
            # Decode name
            z = name.find(b'\x00')
            entry_name = name[:z if z >= 0 else len(name)].decode('ascii')
            
            entry = PakEntry(
                entry_name, profile, color_count, width, height, stride,
                pal_len, data_len, pal_off, data_off
            )
            self._entries.append(entry)

    def find_entries_by_prefix(self, prefix):
        """Find all entries that start with the given prefix"""
        if self._entries is None:
            self._load_index()
            
        return [entry for entry in self._entries if entry.name.startswith(prefix)]

    def get_entry_by_name(self, name):
        """Get a specific entry by exact name"""
        if self._entries is None:
            self._load_index()
            
        for entry in self._entries:
            if entry.name == name:
                return entry
        return None

    def _ensure_buffers(self, pal_len, dat_len):
        """Ensure buffers are large enough"""
        if self._pal_buf is None or len(self._pal_buf) < pal_len:
            self._pal_buf = bytearray(pal_len)
        if self._dat_buf is None or len(self._dat_buf) < dat_len:
            self._dat_buf = bytearray(dat_len)

    def load_entry_data(self, entry):
        """Load palette and data into buffers, return memoryviews"""
        if not self._file:
            raise RuntimeError("PAK file is not open")
            
        self._ensure_buffers(entry.palette_len, entry.data_len)
        
        # Read palette
        self._file.seek(entry.palette_off)
        self._file.readinto(memoryview(self._pal_buf)[:entry.palette_len])
        
        # Read data
        self._file.seek(entry.data_off)
        self._file.readinto(memoryview(self._dat_buf)[:entry.data_len])
        
        mv_pal = memoryview(self._pal_buf)[:entry.palette_len]
        mv_dat = memoryview(self._dat_buf)[:entry.data_len]
        
        return mv_pal, mv_dat

    def draw_entry(self, entry, x, y):
        """Draw a single entry at the specified coordinates"""
        try:
            mv_pal, mv_dat = self.load_entry_data(entry)

            # hex_str = ' '.join([f'{b:02x}' for b in mv_pal])
            # hex_dat = ' '.join([f'{b:02x}' for b in mv_dat])
            # print(f"{entry.name} pal: [ {hex_str} ]")
            # print(f"{entry.name} dat: [ {hex_dat} ]")

            # print(f"{entry.name} ", {
            #     "profile": entry.profile,
            #     "color_count": entry.color_count,
            #     "width": entry.width,
            #     "height": entry.height,
            #     "stride": entry.stride,
            # })
            
            # Create image object
            img = gint.image(
                entry.profile,
                entry.color_count,
                entry.width,
                entry.height,
                entry.stride,
                mv_dat,
                mv_pal
            )
            
            # Draw to screen
            gint.dimage(x, y, img)
            
            # Clean up image immediately
            del img
            
            return True
        except Exception as e:
            print("Error drawing entry {}: {}".format(entry.name, e))
            return False

    def close(self):
        """Close the PAK file"""
        if self._file:
            try:
                self._file.close()
            except:
                pass
            self._file = None

    def __enter__(self):
        """Context manager entry"""
        if not self._file:
            self._open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures file is closed"""
        self.close()
        # Don't suppress exceptions
        return False

    def __del__(self):
        self.close()

class PakProxy:
    """
    A proxy for loading and drawing PAK files on demand.
    Similar to ModuleProxy but for PAK files.
    """
    def __init__(self):
        self._loaded_paks = {}  # Cache of loaded PAK files

    def _get_pak(self, pak_name):
        """Get or create a PakFile instance"""
        if pak_name not in self._loaded_paks:
            self._loaded_paks[pak_name] = PakFile(pak_name)
        return self._loaded_paks[pak_name]

    def draw_from(self, x, y, pak_name, name_prefix, max_width=320):
        """
        Draw tiles from a PAK file that match a name prefix.
        Tiles are drawn in a grid starting at (x,y).
        Line breaks occur when the next tile would exceed max_width.
        """
        try:
            # Use context manager to ensure file is properly closed
            with self._get_pak(pak_name) as pak:
                entries = pak.find_entries_by_prefix(name_prefix)
                
                if not entries:
                    print("No entries found with prefix '{}' in {}".format(name_prefix, pak_name))
                    return 0
                    
                current_x = x
                current_y = y
                drawn_count = 0
                
                for i, entry in enumerate(entries):
                    # Check if we need to break to next line
                    if current_x + entry.width > max_width and current_x > x:
                        # Move to next line
                        current_x = x
                        current_y += entry.height
                    
                    # Draw the entry
                    if pak.draw_entry(entry, current_x, current_y):
                        drawn_count += 1
                    else:
                        print("Failed to draw {}".format(entry.name))
                    
                    # Move to next position
                    current_x += entry.width
                    
                    # Periodic cleanup
                    if i % 5 == 0:
                        gc.collect()
                
                # Update display
                try:
                    gint.dupdate()
                except:
                    pass
                    
                return drawn_count
                
        except Exception as e:
            print("Error in draw_from: {}".format(e))
            import traceback
            traceback.print_exc()
            return 0

    def draw_single(self, x, y, pak_name, entry_name):
        """Draw a single entry by exact name"""
        try:
            # Use context manager to ensure file is properly closed
            with self._get_pak(pak_name) as pak:
                entry = pak.get_entry_by_name(entry_name)
                
                if not entry:
                    print("Entry '{}' not found in {}".format(entry_name, pak_name))
                    return False
                    
                result = pak.draw_entry(entry, x, y)
                if result:
                    try:
                        gint.dupdate()
                    except:
                        pass
                return result
                
        except Exception as e:
            print("Error in draw_single: {}".format(e))
            return False

    def list_entries(self, pak_name, prefix=None):
        """List all entries in a PAK file, optionally filtered by prefix"""
        # try:
        with self._get_pak(pak_name) as pak:
            if prefix:
                entries = pak.find_entries_by_prefix(prefix)
                print("Entries in {} matching '{}':".format(pak_name, prefix))
            else:
                if pak._entries is None:
                    pak._load_index()
                entries = pak._entries
                print("All entries in {}:".format(pak_name))
            
            for i, entry in enumerate(entries):
                print("  {}: {} ({}x{})".format(i, entry.name, entry.width, entry.height))
                
            return len(entries)
        # except Exception as e:
        #     print("Error listing entries in {}: {}".format(pak_name, e))
        #     return 0

    def clear_cache(self):
        """Clear the PAK file cache"""
        for pak in self._loaded_paks.values():
            try:
                pak.close()
            except:
                pass
        self._loaded_paks.clear()

# Global instance
pakloader = PakProxy()

# Convenience functions
def draw_from(x, y, pak_name, name_prefix, max_width=320):
    """Draw tiles from a PAK file that match a name prefix"""
    return pakloader.draw_from(x, y, pak_name, name_prefix, max_width)

def draw_single(x, y, pak_name, entry_name):
    """Draw a single entry by exact name"""
    return pakloader.draw_single(x, y, pak_name, entry_name)

def list_entries(pak_name, prefix=None):
    """List entries in a PAK file"""
    return pakloader.list_entries(pak_name, prefix)

def clear_cache():
    """Clear the PAK loader cache"""
    pakloader.clear_cache()

# Example usage function
def test_pak_loader():
    """Test the PAK loader functionality"""
    mem_before = mem_used()
    print("PAK Loader Test")
    print("Memory before: {} bytes".format(mem_before))
    

    # List entries in tiles.pak
    count = list_entries('faces.pak', 'face2_')
    print("Found {} profile entries".format(count))
    
    # Draw profile entries
    if count > 0:
        drawn = draw_from(10, 60, 'faces.pak', 'face2_', 80)
        # print("Drew {} profile entries".format(drawn))
    
    # Wait for keypress
    gint.getkey()
    
    mem_after = mem_used()
    print("Memory after: {} bytes".format(mem_after))
    print("Memory used: {} bytes".format(mem_after - mem_before))
    
    # Cleanup
    clear_cache()
    gc.collect()

test_pak_loader()