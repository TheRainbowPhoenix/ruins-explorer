import struct
import gc

# ---- structs (little-endian)
_HDR = struct.Struct('<4sHHII')           # magic, version, count, index_off, reserved
_ENT = struct.Struct('<32sBBHHHHHIIII')    # see layout above

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
        magic, version, count, index_off, _ = _HDR.unpack(f.read(_HDR.size))
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
            raw = f.read(_ENT.size)
            (name, _r0, _r1, color_count, width, height, stride, _r2,
             pal_len, data_len, pal_off, data_off) = _ENT.unpack(raw)
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

    def draw_once(self, name, x, y, gint):
        """Load -> construct gint.image -> draw -> release the *image* object.
           Buffers are kept for reuse (fast, low-fragmentation)."""
        entry = self.find(name)
        if not entry:
            raise KeyError(name)

        mv_pal, mv_dat = self.load_into_buffers(entry, want_reuse=True)

        # Build the transient image object; only small Python headers are allocated here.
        img = gint.dimage(
            entry['profile'],
            entry['color_count'],
            entry['width'],
            entry['height'],
            entry['stride'],
            mv_dat,
            mv_pal
        )

        # Draw to VRAM / screen (whatever your API expects)
        gint.draw(x, y, img)

        # Drop the temporary Python object (buffers remain for reuse)
        del img
        gc.collect()

    def draw_and_free_memory(self, name, x, y, gint):
        """Same as draw_once but also frees the buffers to reclaim heap."""
        entry = self.find(name)
        if not entry:
            raise KeyError(name)

        mv_pal, mv_dat = self.load_into_buffers(entry, want_reuse=False)

        img = gint.dimage(
            entry['profile'],
            entry['color_count'],
            entry['width'],
            entry['height'],
            entry['stride'],
            mv_dat,
            mv_pal
        )

        gint.dimage(x, y, img)
        # Free everything
        del img, mv_pal, mv_dat, self._pal_buf, self._data_buf
        self._pal_buf = None
        self._data_buf = None
        gc.collect()


import gint

pak = PakReader('backgrounds.pak')

# Draw and keep buffers for next time (fastest, least fragmentation):
pak.draw_once('background_12', 0, 0, gint)

# Later, another image reuses the same buffers (no big allocs):
pak.draw_once('menu', 0, 0, gint)

# If you need to claw back RAM immediately after a one-off draw:
pak.draw_and_free_memory('splash', 0, 0, gint)

pak.close()
gc.collect()
