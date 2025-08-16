# make_pak_three.py  — run on your PC (CPython)
import struct, sys, types

# ---- PAK layout (same as before) ----
_HDR = struct.Struct('<4sHHII')
_ENT = struct.Struct('<32sBBHHHHHIIII')

def pack(out_path, entries):
    with open(out_path, 'wb') as f:
        f.write(_HDR.pack(b'GIPK', 1, len(entries), 0, 0))  # placeholder (index_off=0)

        blobs = []
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

        index_off = f.tell()
        for b in blobs:
            f.write(_ENT.pack(*b))

        # patch header with index offset
        f.seek(8)
        f.write(struct.pack('<I', index_off))

# ---- stub 'gint' so importing your assets won't try to use the real one ----
# gint_stub = types.ModuleType('gint')
# def _stub_image(*args, **kwargs): return None
# gint_stub.image = _stub_image
# sys.modules.setdefault('gint', gint_stub)

# ---- import the three asset modules (relative first, fall back to absolute) ----
try:
    from . import convertme as m_convertme
    from . import pixelized_2_2 as m_pixelized_2_2
    from . import gui_old as m_gui_old
except ImportError:
    import convertme as m_convertme
    import pixelized_2_2 as m_pixelized_2_2
    import gui_old as m_gui_old

def entry_from_module(mod, name=None):
    """Build a PAK entry dict from a module that defines:
       profile, color_count, width, height, stride, data, pal (or palette)."""
    pal = getattr(mod, 'pal', None)
    if pal is None:
        pal = getattr(mod, 'palette')
    if pal is None:
        raise RuntimeError(f"{mod.__name__} must define 'pal' or 'palette'")

    data = getattr(mod, 'data')
    meta = {
        'profile': getattr(mod, 'profile'),
        'color_count': getattr(mod, 'color_count'),
        'width': getattr(mod, 'width'),
        'height': getattr(mod, 'height'),
        'stride': getattr(mod, 'stride'),
    }

    # sanity check (optional)
    expected = meta['stride'] * meta['height']
    if len(data) != expected:
        print(f"Warning [{mod.__name__}]: data len {len(data)} != stride*height {expected}")

    return {
        'name': name or mod.__name__.split('.')[-1],
        **meta,
        'palette': pal,
        'data': data,
    }

# ---- build entries ----
entries = [
    entry_from_module(m_convertme,     'convertme'),
    entry_from_module(m_pixelized_2_2, 'pixelized_2_2'),
    entry_from_module(m_gui_old,       'gui_old'),
]

# ---- write PAK ----
out_path = 'backgrounds.pak' if len(sys.argv) < 2 else sys.argv[1]
pack(out_path, entries)
print(f"OK: wrote {out_path} with {len(entries)} entries: "
      + ", ".join(e['name'] for e in entries))
