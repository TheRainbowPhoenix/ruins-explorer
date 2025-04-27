from PIL import Image
import numpy as np
from collections import Counter
from IPython.display import display

# 1. Load the UI image and extract its top 64 most frequent colors
ui_img = Image.open('GAME_UI.png').convert('RGB')
palette = [color for color, _ in Counter(ui_img.getdata()).most_common(64)]

# Sort palette by brightness for consistent ordering (not strictly necessary)
def brightness(rgb):
    r, g, b = rgb
    return int(0.299*r + 0.587*g + 0.114*b + 0.5)
palette_sorted = sorted(palette, key=brightness)

# 2. Load the source image
src = Image.open('convert_me.png').convert('RGBA')
w, h = src.size
src_pixels = np.array(src)  # shape (h, w, 4)

# 3. Compute brightness histogram for opaque pixels
rgb = src_pixels[..., :3]
alpha = src_pixels[..., 3]
brightness_map = np.dot(rgb, [0.299, 0.587, 0.114]).astype(int)
mask = alpha >= 128

# Histogram & cumulative histogram
hist = np.bincount(brightness_map[mask], minlength=256)
cum = np.cumsum(hist)
total = cum[-1] if cum[-1] > 0 else 1

# 4. Create mapping from brightness value to palette index (equalized)
palette_count = len(palette_sorted)
cdf = cum / total
index_map = np.round(cdf * (palette_count - 1)).astype(int)

# 5. Apply brightness-equalized 64-color mapping
mapped = Image.new('RGBA', (w, h))
mapped_px = mapped.load()

for y in range(h):
    for x in range(w):
        pr, pg, pb, pa = src_pixels[y, x]
        if pa < 128:
            mapped_px[x, y] = (pr, pg, pb, pa)
        else:
            b_val = brightness_map[y, x]
            idx = index_map[b_val]
            nr, ng, nb = palette_sorted[idx]
            mapped_px[x, y] = (nr, ng, nb, pa)

# 6. Helper: find nearest palette color by Euclidean distance in RGB
def nearest_color(rgb, palette):
    r, g, b = rgb
    return min(palette, key=lambda p: (p[0]-r)**2 + (p[1]-g)**2 + (p[2]-b)**2)

# 7. Pixelizer: block-average then quantize to nearest palette entry
def pixelize(img, block):
    w, h = img.size
    arr = np.array(img)  # (h, w, 4)
    out = Image.new('RGBA', img.size)
    out_px = out.load()
    for by in range(0, h, block):
        for bx in range(0, w, block):
            block_pixels = arr[by:by+block, bx:bx+block]
            # average RGBA
            avg = block_pixels.reshape(-1, 4).mean(axis=0).astype(int)
            # find nearest palette RGB
            nearest_rgb = nearest_color(tuple(avg[:3]), palette_sorted)
            fill = (nearest_rgb[0], nearest_rgb[1], nearest_rgb[2], int(avg[3]))
            # fill block
            for yy in range(by, min(by+block, h)):
                for xx in range(bx, min(bx+block, w)):
                    out_px[xx, yy] = fill
    return out

# 8. Display original, equalized, and pixelized variants
display(src)
display(mapped)
mapped.save(f"mapped.png")

for size in (2, 4, 8):
    print(f"Pixelized {size}×{size}:")
    p = pixelize(mapped, size)
    p.save(f"pixelized_{size}_{size}.png")

