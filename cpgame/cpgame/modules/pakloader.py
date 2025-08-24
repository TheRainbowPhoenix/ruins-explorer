# cpgame/modules/pakloader.py
# A dynamic PAK file loader for loading and drawing image tiles on the fly.

import gc
import struct
from micropython import const

try:
    import gint
except:
    pass

try:
    from typing import Optional, Any, Dict, List
except:
    pass


# ---- PAK Format structs (little-endian)
HDR_FMT = const('<4sHHII')                # magic, version, count, index_off, reserved
ENT_FMT = const('<32sBBHHHHHIIII')        # name[32], profile,u8,res,u8,cc,u16,w,h,stride,res,u16, plen,u32,dlen,u32, poff,u32, doff,u32
HDR_SIZE = const(16)
ENT_SIZE = const(60)

class PakFile:
    """Represents an open PAK file with on-the-fly entry processing"""
    def __init__(self, filepath):
        self.filepath = filepath
        self._file = None
        self._count = 0
        self._index_off = 0
        self._pal_buf = None
        self._dat_buf = None
        self._hdr_buf = None
        self._ent_buf = None
        self._entry_map = None  # Map of name -> entry data for ordered drawing
        self._open()

    def _open(self):
        """Open the PAK file and read header"""
        try:
            self._file = open(self.filepath, 'rb')
            # Pre-allocate header buffer
            self._hdr_buf = bytearray(HDR_SIZE)
            hdr_mv = memoryview(self._hdr_buf)
            
            # Read header using memoryview
            self._file.readinto(hdr_mv)
            magic, version, count, index_off, _ = struct.unpack(HDR_FMT, hdr_mv)
            
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

    def _ensure_buffers(self, pal_len, dat_len):
        """Ensure buffers are large enough"""
        if self._pal_buf is None or len(self._pal_buf) < pal_len:
            self._pal_buf = bytearray(pal_len)
        if self._dat_buf is None or len(self._dat_buf) < dat_len:
            self._dat_buf = bytearray(dat_len)

    def _load_entry_data(self, palette_off, palette_len, data_off, data_len):
        """Load palette and data into buffers, return memoryviews"""
        if not self._file:
            raise RuntimeError("PAK file is not open")
            
        self._ensure_buffers(palette_len, data_len)
        
        # Read palette using memoryviews
        self._file.seek(palette_off)
        pal_mv = memoryview(self._pal_buf)
        self._file.readinto(pal_mv[:palette_len])
        
        # Read data using memoryviews
        self._file.seek(data_off)
        dat_mv = memoryview(self._dat_buf)
        self._file.readinto(dat_mv[:data_len])
        
        return pal_mv[:palette_len], dat_mv[:data_len]

    def _draw_entry_raw(self, profile, color_count, width, height, stride, 
                       palette_off, palette_len, data_off, data_len, x, y):
        """Draw an entry directly from raw data without creating PakEntry objects"""
        try:
            mv_pal, mv_dat = self._load_entry_data(palette_off, palette_len, data_off, data_len)

            # Create image object
            # img = gint.image(
            #     profile,
            #     color_count,
            #     width,
            #     height,
            #     stride,
            #     mv_dat,
            #     mv_pal
            # )
            img = gint.image(
                profile,
                color_count,
                width,
                height,
                stride,
                mv_dat,
                mv_pal
            )
            
            # Draw to screen
            gint.dimage(x, y, img)
            
            # Clean up image immediately
            del img
            
            return True
        except Exception as e:
            print("Error drawing entry at ({},{}): {}".format(x, y, e))
            return False

    def _build_entry_map(self, name_prefix=None):
        """Build a map of entry names to their data for ordered processing"""
        if self._entry_map is not None:
            return
            
        try:
            if not self._file:
                raise RuntimeError("PAK file is not open")
                
            # Pre-allocate entry buffer
            if self._ent_buf is None:
                self._ent_buf = bytearray(ENT_SIZE)
            ent_mv = memoryview(self._ent_buf)
            
            # Seek to index
            self._file.seek(self._index_off)
            
            self._entry_map = {}
            
            for _ in range(self._count):
                # Read entry using memoryview (no copy)
                bytes_read = self._file.readinto(ent_mv)
                if bytes_read < ENT_SIZE:
                    break
                
                # Unpack directly from memoryview
                (name, profile, _r1, color_count, width, height, stride, _r2,
                 pal_len, data_len, pal_off, data_off) = struct.unpack(ENT_FMT, ent_mv)
                
                # Decode name
                z = name.find(b'\x00')
                entry_name = name[:z if z >= 0 else len(name)].decode('ascii')
                
                # Store only entries matching prefix (or all if no prefix)
                if name_prefix is None or entry_name.startswith(name_prefix):
                    self._entry_map[entry_name] = (
                        profile, color_count, width, height, stride,
                        pal_off, pal_len, data_off, data_len
                    )
            
        except Exception as e:
            print("Error building entry map: {}".format(e))
            self._entry_map = {}

    def draw_entries_by_prefix(self, x, y, name_prefix, max_width=320):
        """Draw tiles using pre-built entry map for ordered drawing"""
        try:
            if not self._file:
                raise RuntimeError("PAK file is not open")
                
            # Build entry map if not already built
            self._build_entry_map(name_prefix)
            
            current_x = x
            current_y = y
            drawn_count = 0
            
            # Process entries in sorted order
            sorted_names = sorted(self._entry_map.keys())
            
            for entry_name in sorted_names:
                entry_data = self._entry_map[entry_name]
                (profile, color_count, width, height, stride,
                 pal_off, pal_len, data_off, data_len) = entry_data
                
                # Check if we need to break to next line
                if current_x + width > max_width and current_x > x:
                    # Move to next line
                    current_x = x
                    current_y += height
                
                # Draw the entry directly
                if self._draw_entry_raw(profile, color_count, width, height, stride,
                                      pal_off, pal_len, data_off, data_len,
                                      current_x, current_y):
                    drawn_count += 1
                
                # Move to next position
                current_x += width
                
                # Periodic cleanup
                if drawn_count % 5 == 0:
                    gc.collect()
            
            # Update display
            # try:
            #     gint.dupdate()
            # except:
            #     pass
                
            return drawn_count
            
        except Exception as e:
            print("Error in draw_entries_by_prefix: {}".format(e))
            return 0

    def draw_single_entry(self, x, y, entry_name):
        """Draw a single entry by exact name"""
        try:
            if not self._file:
                raise RuntimeError("PAK file is not open")
                
            # Build entry map for all entries to find the specific one
            if self._entry_map is None:
                self._build_entry_map()
                
            if entry_name not in self._entry_map:
                print("Entry '{}' not found".format(entry_name))
                return False
                
            entry_data = self._entry_map[entry_name]
            (profile, color_count, width, height, stride,
             pal_off, pal_len, data_off, data_len) = entry_data
            
            # Draw the entry directly
            result = self._draw_entry_raw(profile, color_count, width, height, stride,
                                        pal_off, pal_len, data_off, data_len, x, y)
            if result:
                try:
                    gint.dupdate()
                except:
                    pass
            return result
            
        except Exception as e:
            print("Error in draw_single_entry: {}".format(e))
            return False

    def list_entries(self, prefix=None):
        """List entries on-the-fly without storing them"""
        try:
            if not self._file:
                raise RuntimeError("PAK file is not open")
                
            # Build entry map
            self._build_entry_map(prefix)
            
            # List entries in sorted order
            sorted_names = sorted(self._entry_map.keys())
            
            # for i, name in enumerate(sorted_names):
            #     print("  {}: {}".format(i, name))
                
            return len(sorted_names)
            
        except Exception as e:
            print("Error listing entries: {}".format(e))
            return 0

    def close(self):
        """Close the PAK file and clean up buffers"""
        if self._file:
            try:
                self._file.close()
            except:
                pass
            self._file = None
        
        # Clean up buffers to free memory
        self._file = None
        self._count = None
        self._index_off = None
        self._pal_buf = None
        self._dat_buf = None
        self._hdr_buf = None
        self._ent_buf = None
        self._entry_map = None

    def __enter__(self):
        """Context manager entry"""
        if not self._file:
            self._open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures file is closed and memory is freed"""
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
        Tiles are drawn using pre-built entry map for ordered drawing.
        """
        try:
            # Use context manager to ensure file is properly closed
            with self._get_pak(pak_name) as pak:
                return pak.draw_entries_by_prefix(x, y, name_prefix, max_width)
        except Exception as e:
            print("Error in draw_from: {}".format(e))
            # import traceback
            # traceback.print_exc()
            return 0

    def draw_single(self, x, y, pak_name, entry_name):
        """Draw a single entry by exact name"""
        try:
            # Use context manager to ensure file is properly closed
            with self._get_pak(pak_name) as pak:
                return pak.draw_single_entry(x, y, entry_name)
        except Exception as e:
            print("Error in draw_single: {}".format(e))
            return False

    def list_entries(self, pak_name, prefix=None):
        """List all entries in a PAK file, optionally filtered by prefix"""
        try:
            with self._get_pak(pak_name) as pak:
                # if prefix:
                #     print("Entries in {} matching '{}':".format(pak_name, prefix))
                # else:
                #     print("All entries in {}:".format(pak_name))
                return pak.list_entries(prefix)
        except Exception as e:
            print("Error listing entries in {}: {}".format(pak_name, e))
            return 0

    def clear_cache(self):
        """Clear the PAK file cache"""
        for pak in self._loaded_paks.values():
            try:
                pak.close()
            except:
                pass
        self._loaded_paks.clear()
        gc.collect()

    def destroy(self):
        self.clear_cache()
