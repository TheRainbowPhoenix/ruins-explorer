# tile_draw.py
import sys, gc, gint

TILE_SIZE = 16

def _screen_size():
    try:
        return gint.DWIDTH, gint.DHEIGHT      # if your port exposes these
    except Exception:
        return 320, 528                       # fallback

def _import_image_module(modname):
    return __import__(modname, None, None, ('image',))

def _cleanup_module(mod, img=None):
    # Drop local refs first
    try:
        if img is not None:
            del img
    except:
        pass
    # Remove the heavy attribute from the module
    try:
        if hasattr(mod, 'image'):
            delattr(mod, 'image')
    except:
        pass
    # Uncache the module so it can be GC'd
    name = getattr(mod, '__name__', None)
    if name:
        sys.modules.pop(name, None)
    # Drop the module object itself
    try:
        del mod
    except:
        pass
    gc.collect()

def draw_tilemap_fullscreen_from_module(modname, tilemap=None, x0=0, y0=0, tile_size=TILE_SIZE, blank_index=-1):
    """Import a tileset module containing `image`, draw the full-screen tilemap, then unload it."""
    mod = _import_image_module(modname)
    try:
        tileset = mod.image  # large object—keep scope tight
        screen_w, screen_h = _screen_size()
        cols = screen_w // tile_size
        rows = screen_h // tile_size

        tiles_per_row = tileset.width  // tile_size
        tiles_per_col = tileset.height // tile_size
        total_tiles   = tiles_per_row * tiles_per_col

        dsubimage = gint.dsubimage
        dupdate   = gint.dupdate

        if tilemap is None:
            # AUTO: generate indices on the fly, minimal RAM
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
                dupdate()  # per row
        else:
            # EXPLICIT: use provided tilemap
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
                dupdate()  # per row
    finally:
        _cleanup_module(mod, img=locals().get('tileset'))

def draw_fullscreen_image_from_module(modname, x=0, y=0):
    """Import a fullscreen image module containing `image`, draw it, then unload it."""
    mod = _import_image_module(modname)
    try:
        img = mod.image
        # Use whatever your API is: gint.draw or gint.dimage
        try:
            gint.dimage(x, y, img)
        except AttributeError:
            pass
        gint.dupdate()
    finally:
        _cleanup_module(mod, img=locals().get('img'))


# -------- examples --------
# 1) draw tilemap from a big tileset module, then free it
draw_tilemap_fullscreen_from_module('flappy_img')

# 2) draw four huge fullscreen images one by one, cleaning after each
for name in ('a_img', 'b_img', 'c_img', 'd_img', 'a_img', 'b_img', 'c_img', 'd_img'):
    # draw_tilemap_fullscreen_from_module(name)
    draw_fullscreen_image_from_module(name)
#     # optionally: gint.getkey()  # pause, then next
gint.getkey()

