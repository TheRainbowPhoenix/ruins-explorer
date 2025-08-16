# tile_draw.py
import sys, gc, gint
import time  # MicroPython exposes ticks_* here

# ---------------- core drawing ----------------

def _screen_size():
    try:
        return gint.DWIDTH, gint.DHEIGHT
    except Exception:
        return 320, 528

def _import_image_module(modname):
    # Import module and expose its 'image' attribute
    return __import__(modname, None, None, ('image',))

def _cleanup_module(mod, img=None):
    try:
        if img is not None:
            del img
    except:
        pass
    try:
        if hasattr(mod, 'image'):
            delattr(mod, 'image')
    except:
        pass
    name = getattr(mod, '__name__', None)
    if name:
        sys.modules.pop(name, None)
    try:
        del mod
    except:
        pass
    gc.collect()

def draw_tilemap_fullscreen_from_module(modname, tilemap=None, x0=0, y0=0, tile_size=16, blank_index=-1):
    """Import a tileset module containing `image`, draw full-screen, then unload it."""
    mod = _import_image_module(modname)
    try:
        tileset = mod.image
        screen_w, screen_h = _screen_size()
        cols = screen_w // tile_size
        rows = screen_h // tile_size

        tiles_per_row = tileset.width  // tile_size
        tiles_per_col = tileset.height // tile_size
        total_tiles   = tiles_per_row * tiles_per_col

        dsubimage = gint.dsubimage
        dupdate   = gint.dupdate

        if tilemap is None:
            idx = 0
            for ty in range(rows):
                dy = y0 + ty * tile_size
                for tx in range(cols):
                    dx = x0 + tx * tile_size
                    t = idx % total_tiles
                    if t != blank_index:
                        sx = (t % tiles_per_row) * tile_size
                        sy = (t // tiles_per_row) * tile_size
                        dsubimage(dx, dy, tileset, sx, sy, tile_size, tile_size)
                    idx += 1
                dupdate()  # update per row (faster and less flicker than per tile)
        else:
            for ty in range(rows):
                row = tilemap[ty]
                dy = y0 + ty * tile_size
                for tx in range(cols):
                    t = row[tx]
                    if t == blank_index:
                        continue
                    t %= total_tiles
                    dx = x0 + tx * tile_size
                    sx = (t % tiles_per_row) * tile_size
                    sy = (t // tiles_per_row) * tile_size
                    dsubimage(dx, dy, tileset, sx, sy, tile_size, tile_size)
                dupdate()
    finally:
        _cleanup_module(mod, img=locals().get('tileset'))

def draw_fullscreen_image_from_module(modname, x=0, y=0):
    """Import a fullscreen image module containing `image`, draw it, then unload it."""
    mod = _import_image_module(modname)
    try:
        img = mod.image
        try:
            gint.dimage(x, y, img)
        except AttributeError:
            pass
        gint.dupdate()
    finally:
        _cleanup_module(mod, img=locals().get('img'))

# ---------------- benchmarking ----------------

def _ticks():
    return time.ticks_ms()

def _ticks_diff(a, b):
    # returns a - b handling wrap
    return time.ticks_diff(a, b)

def bench_modules(mod_names, tile_sizes=(8, 12, 16, 24, 32), repeat=1):
    """
    For each TILE SIZE, draw all modules in mod_names (load→draw→unload for each),
    measure total time in ms. 'repeat' lets you loop the 8-image sequence N times.
    """
    screen_w, screen_h = _screen_size()
    # print("Screen:", screen_w, "x", screen_h)
    # print("Modules:", mod_names)
    # print("Repeats:", repeat)
    results = []

    # Optional: warm-up GC and display to stabilize timing a bit
    gc.collect()
    try:
        gint.dupdate()
    except:
        pass
    
    out = ""
    for ts in tile_sizes:
        gc.collect()
        t0 = _ticks()
        for _ in range(repeat):
            for name in mod_names:
                # Prefer the tilemap-based renderer (your faster path)
                draw_tilemap_fullscreen_from_module(name, tile_size=ts)
        t1 = _ticks()
        elapsed = _ticks_diff(t1, t0)

        cols = screen_w // ts
        rows = screen_h // ts
        tiles_per_screen = cols * rows
        total_tiles = tiles_per_screen * len(mod_names) * repeat
        tiles_per_sec = (total_tiles * 1000) // elapsed if elapsed > 0 else 0

        results.append((ts, elapsed, total_tiles, tiles_per_sec))
        out += ("TILE_SIZE=%d -> %d ms for %d tiles (~%d tiles/s)" %
              (ts, elapsed, total_tiles, tiles_per_sec))
    print(out)
    return results

# ---------------- run ----------------


mods = ('a_img', 'b_img', 'c_img', 'd_img', 'a_img', 'b_img', 'c_img', 'd_img')

# Try a few tile sizes; adjust as you like
sizes = (8, 12, 16, 24, 32, 64)

results = bench_modules(mods, tile_sizes=sizes, repeat=1)

print("\nSummary:")
for ts, ms, tiles, tps in results:
    print("  %2d px: %6d ms, %d tiles total, ~%d tiles/s" % (ts, ms, tiles, tps))

# pause so you can see the last frame on-screen if desired
try:
    gint.getkey()
except:
    pass
