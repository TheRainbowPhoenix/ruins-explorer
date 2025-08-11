import gint

def dtextured_border(x0: int, y0: int, x1: int, y1: int, img, PATCH_BORDER):
    """
    Draw a 9-patch border around the rectangle [x0,y0,x1,y1] from 'img', 
    using the slices defined in PATCH_BORDER.
    """
    # unpack corner sizes
    tl_w, tl_h = PATCH_BORDER['tl'][2:]
    tr_w, tr_h = PATCH_BORDER['tr'][2:]
    bl_w, bl_h = PATCH_BORDER['bl'][2:]
    br_w, br_h = PATCH_BORDER['br'][2:]

    # ---- Corners ----
    sx, sy, w, h = PATCH_BORDER['tl']
    gint.dsubimage(x0,         y0,          img, sx, sy, w, h)
    sx, sy, w, h = PATCH_BORDER['tr']
    gint.dsubimage(x1 - w + 1, y0,          img, sx, sy, w, h)
    sx, sy, w, h = PATCH_BORDER['bl']
    gint.dsubimage(x0,         y1 - h + 1,  img, sx, sy, w, h)
    sx, sy, w, h = PATCH_BORDER['br']
    gint.dsubimage(x1 - w + 1, y1 - h + 1,  img, sx, sy, w, h)

    # ---- Edges (tiled) ----
    # Top
    sx, sy, ew, eh = PATCH_BORDER['t']
    for xx in range(x0 + tl_w, x1 - tr_w + 1, ew):
        gint.dsubimage(xx, y0, img, sx, sy, ew, eh)

    # Bottom
    sx, sy, ew, eh = PATCH_BORDER['b']
    by = y1 - eh + 1
    for xx in range(x0 + bl_w, x1 - br_w + 1, ew):
        gint.dsubimage(xx, by, img, sx, sy, ew, eh)

    # Left
    sx, sy, ew, eh = PATCH_BORDER['l']
    for yy in range(y0 + tl_h, y1 - bl_h + 1, eh):
        gint.dsubimage(x0, yy, img, sx, sy, ew, eh)

    # Right
    sx, sy, ew, eh = PATCH_BORDER['r']
    rx = x1 - ew + 1
    for yy in range(y0 + tr_h, y1 - br_h + 1, eh):
        gint.dsubimage(rx, yy, img, sx, sy, ew, eh)