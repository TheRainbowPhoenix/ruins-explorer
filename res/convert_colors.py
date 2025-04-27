from PIL import Image
import numpy as np
from collections import Counter

# 1. Load the UI image and extract its top 64 most frequent colors
ui_img = Image.open('GAME_UI.png').convert('RGB')
palette = [color for color, _ in Counter(ui_img.getdata()).most_common(64)]
# Sort palette by brightness (0-255)
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
# Compute brightness map for each pixel
brightness_map = np.dot(rgb, [0.299, 0.587, 0.114]).astype(int)
# Mask of opaque pixels
mask = alpha >= 128

# Histogram of brightness values 0-255 for opaque pixels
hist = np.bincount(brightness_map[mask], minlength=256)
# Cumulative histogram
cum = np.cumsum(hist)
total = cum[-1]

# 4. Create mapping from brightness value to palette index
palette_count = len(palette_sorted)
# Avoid zero division
if total == 0:
    total = 1
# Compute CDF mapping to palette indices
# For each brightness level b: cdf = cum[b]/total, index = round(cdf*(n-1))
cdf = cum / total
index_map = np.round(cdf * (palette_count - 1)).astype(int)  # shape (256,)

# 5. Apply mapping to each pixel
result = Image.new('RGBA', (w, h))
res_pixels = result.load()

for y in range(h):
    for x in range(w):
        pr, pg, pb, pa = src_pixels[y, x]
        if pa < 128:
            res_pixels[x, y] = (pr, pg, pb, pa)
        else:
            b_val = brightness_map[y, x]
            palette_idx = index_map[b_val]
            nr, ng, nb = palette_sorted[palette_idx]
            res_pixels[x, y] = (nr, ng, nb, pa)

# 6. Save the result to a new file
output_filename = 'image_19_palette_swapped.png'
result.save(output_filename)
print(f"Result saved to {output_filename}")