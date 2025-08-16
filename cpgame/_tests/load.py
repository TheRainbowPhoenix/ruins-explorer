# loader_pak.py
import struct
import gc
import gint

# ---- Plain struct formats (no Struct objects) ----
HDR_FMT = '<4sHHII'                # magic, version, count, index_off, reserved
HDR_SIZE = 16 # struct.calcsize(HDR_FMT)

ENT_FMT = '<32sBBHHHHHIIII'        # name[32], profile,u8,res,u8,cc,u16,w,h,stride,res,u16, plen,u32,dlen,u32, poff,u32, doff,u32
ENT_SIZE = 60 # struct.calcsize(ENT_FMT)

class PakReader:
    def __init__(self, path):
        self.f = open(path, 'rb')
        self._index = None
        self._count = 0
        self._index_off = 0
        self._load_header()
        # Reusable buffers (only allocated when needed)
        self._data_buf = None
        self._pal_buf = None

    def close(self):
        try:
            self.f.close()
        except:
            pass

    # ---------- internals ----------
    def _load_header(self):
        f = self.f
        f.seek(0)
        magic, version, count, index_off, _ = struct.unpack(HDR_FMT, f.read(HDR_SIZE))
        if magic != b'GIPK' or version != 1:
            raise ValueError('Bad PAK header')
        self._count = count
        self._index_off = index_off

    def _load_index(self):
        if self._index is not None:
            return
        f = self.f
        f.seek(self._index_off)
        idx = []
        for _ in range(self._count):
            (name_bytes, profile, _res1,
             color_count, width, height, stride, _res2,
             pal_len, data_len, pal_off, data_off) = struct.unpack(ENT_FMT, f.read(ENT_SIZE))

            z = name_bytes.find(b'\x00')
            key = name_bytes[:z if z >= 0 else len(name_bytes)].decode('ascii')

            idx.append({
                'name': key,
                'profile': profile,
                'color_count': color_count,
                'width': width,
                'height': height,
                'stride': stride,
                'palette_len': pal_len,
                'data_len': data_len,
                'palette_off': pal_off,
                'data_off': data_off,
            })
        self._index = idx

    # ---------- index/query ----------
    def find(self, name):
        self._load_index()
        if self._index:
            for e in self._index:
                if e['name'] == name:
                    return e
        return None

    # ---------- I/O + draw ----------
    def _read_into_buffers(self, entry, reuse):
        """Read straight into bytearrays; expose memoryviews (no extra copies)."""
        f = self.f
        pal_len = entry['palette_len']
        data_len = entry['data_len']

        if (not reuse) or (self._pal_buf is None) or (len(self._pal_buf) < pal_len):
            self._pal_buf = bytearray(pal_len)
        if (not reuse) or (self._data_buf is None) or (len(self._data_buf) < data_len):
            self._data_buf = bytearray(data_len)

        mv_pal = memoryview(self._pal_buf)[:pal_len]
        mv_dat = memoryview(self._data_buf)[:data_len]

        f.seek(entry['palette_off']); f.readinto(mv_pal)
        f.seek(entry['data_off']);    f.readinto(mv_dat)
        return mv_pal, mv_dat

    def _make_image(self, entry, mv_pal, mv_dat):
        # Create a tiny Python wrapper that *references* the big buffers
        return gint.image(
            entry['profile'],
            entry['color_count'],
            entry['width'],
            entry['height'],
            entry['stride'],
            mv_dat,
            mv_pal
        )

    def draw_and_free(self, name, x, y):
        """Load -> draw -> free image + buffers immediately (lowest peak RAM)."""
        entry = self.find(name)
        if not entry:
            raise KeyError(name)

        # Read fresh buffers sized exactly for this asset
        mv_pal, mv_dat = self._read_into_buffers(entry, reuse=False)
        img = self._make_image(entry, mv_pal, mv_dat)

        # Draw (driver should blit/copy to VRAM; then buffers can be released)
        gint.dimage(x, y, img)
        gint.dupdate()

        # Drop image object and both big buffers; then collect
        del img, mv_pal, mv_dat
        del self._pal_buf, self._data_buf
        self._pal_buf = None
        self._data_buf = None
        gc.collect()

    def draw_reuse(self, name, x, y):
        """Load -> draw, but keep the big buffers for the next asset (faster)."""
        entry = self.find(name)
        if not entry:
            raise KeyError(name)
        mv_pal, mv_dat = self._read_into_buffers(entry, reuse=True)
        img = self._make_image(entry, mv_pal, mv_dat)
        gint.dimage(x, y, img)
        gint.dupdate()
        # Free just the transient objects; keep underlying buffers
        del img, mv_pal, mv_dat
        gc.collect()

# ---------- Example: draw the 3 entries and free after each ----------
def draw_three_and_free(pak_path):
    pak = PakReader(pak_path)
    try:
        # Adjust positions to your layout/screen
        pak.draw_and_free('convertme',      0,   0)
        pak.draw_and_free('pixelized_2_2',  0,  80)
        pak.draw_and_free('gui_old',        0, 160)
    finally:
        pak.close()
        gc.collect()

# Usage:
# draw_three_and_free('backgrounds.pak')


# Call it:

draw_three_and_free('gm/backgrounds.pak')
gint.getkey()

