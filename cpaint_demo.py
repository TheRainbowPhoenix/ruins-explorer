from gint import *
import cgui
import cinput
import struct
import math
import random
import gc
import time

try:
    from micropython import opt_level
    opt_level(3)
except ImportError:
    pass

# =============================================================================
# APP CONFIG
# =============================================================================

SCREEN_W = 320
SCREEN_H = 528
HEADER_H = 50

# Internal Buffer Resolution (Half Size)
BUF_W = 160
BUF_H = (528 - HEADER_H) // 2 # ~239
BUF_HEADER_OFFSET = HEADER_H

# =============================================================================
# IMAGE & BUFFER MANAGEMENT
# =============================================================================

class Canvas:
    def __init__(self):
        # Raw buffer RGB565 (2 bytes per pixel) for half-res
        # Size: 160 * 239 * 2 ~= 76 KB
        # We start with an empty buffer and let clear() allocate it properly
        self.buffer = bytearray()
        self.mv = None
        self.clear(C_WHITE)

    def clear(self, color_int):
        hi = (color_int >> 8) & 0xFF
        lo = color_int & 0xFF
        
        # Optimization: Re-allocate buffer to avoid slow loops or slice assignment issues.
        # This bypasses the 'memoryview/bytearray does not support item assignment' error
        # that occurs when trying to assign to a slice (buffer[start:end] = ...).
        gc.collect()
        try:
            # Construct the full buffer pattern in one go
            # This is fast and efficient in MicroPython
            pix = bytes([lo, hi])
            self.buffer = bytearray(pix * (BUF_W * BUF_H))
            # Keep memoryview if needed for zero-copy reads, though we use buffer directly mostly
            self.mv = memoryview(self.buffer)
        except MemoryError:
            cgui.msgbox("Err: RAM full in Clear")
        
        dclear(color_int)

    def draw_scaled(self):
        # Manually upscale buffer to VRAM using rectangles
        # This is the "slow" pixel perfect 2x scale render
        # Optimization: We interpret 4 bytes from buffer as 2 pixels, 
        # but Python is slow. 
        # Faster strategy: Draw 2x2 rects.
        
        # We can try to use dsubimage if we had a scaler, but we don't.
        # We will loop. To make it slightly faster, we avoid function calls in loop.
        
        # NOTE: This function is slow (seconds). Used only on full redraws.
        buf = self.buffer
        cw = BUF_W
        ch = BUF_H
        
        # dclear(C_WHITE) # Clear bg first
        # Draw header bg? Done by app.
        
        y_screen = BUF_HEADER_OFFSET
        
        # Optimization: drawing line by line?
        # drect is fast in C. Calling it 160*239 = 38k times is the bottleneck.
        # We will warn user or use a "Loading..." placeholder if needed.
        # Actually, for the "Paint" mode, we just keep the VRAM dirty.
        # This function is only called when we restore context (e.g. after menu).
        
        ptr = 0
        for y in range(ch):
            ys = y_screen + y*2
            for x in range(cw):
                lo = buf[ptr]
                hi = buf[ptr+1]
                col = (hi << 8) | lo
                ptr += 2
                
                # Draw 2x2 pixel
                drect(x*2, ys, x*2+1, ys+1, col)
    
    def bake_stroke(self, points, color, size, spacing, spread, flow, opacity, shape):
        # 1. Stroke Path Generation (Interpolation + Spacing + Spread)
        stamps = []
        if not points: return

        # Unpack color
        sr, sg, sb = cgui.unpack_color(color)
        
        # Jitter function
        def get_jitter():
            if spread <= 0: return 0, 0
            jx = random.randint(-int(spread), int(spread))
            jy = random.randint(-int(spread), int(spread))
            return jx, jy

        # Adjust size for half-res buffer (size is in screen pixels 1-50)
        # Buffer pixels are 2x screen pixels.
        # So a 10px brush on screen is 5px on buffer.
        r_buf = max(1, int(size // 4)) # Radius in buffer coords
        r2_buf = r_buf * r_buf
        
        # Spacing is screen pixels, map to buffer
        spacing_buf = max(1.0, spacing / 2.0)
        spread_buf = spread / 2.0

        # Map screen points to buffer points
        # Point (px, py) -> (px // 2, (py - HEADER) // 2)
        b_points = []
        for x, y in points:
            bx = x // 2
            by = (y - BUF_HEADER_OFFSET) // 2
            b_points.append((bx, by))

        # Interpolate
        last_x, last_y = b_points[0]
        jx, jy = get_jitter()
        stamps.append((int(last_x + jx/2), int(last_y + jy/2))) # scaled jitter

        dist_acc = 0.0
        
        for i in range(1, len(b_points)):
            x0, y0 = b_points[i-1]
            x1, y1 = b_points[i]
            
            dx = x1 - x0
            dy = y1 - y0
            seg_len = math.sqrt(dx*dx + dy*dy)
            
            if seg_len == 0: continue
            
            current_dist = 0.0
            while (dist_acc + seg_len) >= spacing_buf:
                step_needed = spacing_buf - dist_acc
                current_dist += step_needed
                
                t = current_dist / seg_len
                px = x0 + dx * t
                py = y0 + dy * t
                
                jx, jy = get_jitter()
                stamps.append((int(px + jx/2), int(py + jy/2)))
                
                dist_acc = 0.0
                seg_len -= step_needed
                x0, y0 = px, py
                dx = x1 - x0
                dy = y1 - y0
                
            dist_acc += seg_len

        # 2. Render Stamps to Buffer
        cw, ch = BUF_W, BUF_H
        
        # Opacity/Flow accumulation logic
        # Simple implementation: blend each stamp.
        alpha_base = (opacity / 100.0) * (flow / 100.0)
        
        # Clamp alpha to avoid issues
        alpha_base = max(0.01, min(1.0, alpha_base))

        if alpha_base >= 0.98:
            is_solid = True
            clo = color & 0xFF
            chi = (color >> 8) & 0xFF
        else:
            is_solid = False

        # Use self.buffer directly to avoid memoryview item assignment issues
        buf = self.buffer

        for cx, cy in stamps:
            # Bounds
            y_min = max(0, cy - r_buf)
            y_max = min(ch, cy + r_buf + 1)
            x_min = max(0, cx - r_buf)
            x_max = min(cw, cx + r_buf + 1)

            for y in range(y_min, y_max):
                dy = y - cy
                
                if shape == 'circle':
                    dy2 = dy*dy
                    rem = r2_buf - dy2
                    if rem < 0: continue
                    dx_limit = int(math.sqrt(rem))
                    row_x_min = max(x_min, cx - dx_limit)
                    row_x_max = min(x_max, cx + dx_limit + 1)
                elif shape == 'square':
                    row_x_min, row_x_max = x_min, x_max
                elif shape == 'rect_v':
                     # Height dominant, width half
                     if abs(dy) > r_buf: continue
                     dx_limit = max(1, r_buf//2)
                     row_x_min = max(x_min, cx - dx_limit)
                     row_x_max = min(x_max, cx + dx_limit + 1)
                elif shape == 'oval':
                     # Width dominant
                     if abs(dy) > max(1, r_buf//2): continue
                     row_x_min = max(x_min, cx - r_buf)
                     row_x_max = min(x_max, cx + r_buf + 1)
                else: 
                     row_x_min, row_x_max = x_min, x_max

                for x in range(row_x_min, row_x_max):
                    idx = (y * cw + x) * 2
                    
                    if is_solid:
                        buf[idx] = clo
                        buf[idx+1] = chi
                    else:
                        dlo = buf[idx]
                        dhi = buf[idx+1]
                        dest_c = (dhi << 8) | dlo
                        dr, dg, db = cgui.unpack_color(dest_c)
                        
                        out_r = int(sr * alpha_base + dr * (1.0 - alpha_base))
                        out_g = int(sg * alpha_base + dg * (1.0 - alpha_base))
                        out_b = int(sb * alpha_base + db * (1.0 - alpha_base))
                        
                        res_c = cgui.pack_color(out_r, out_g, out_b)
                        buf[idx] = res_c & 0xFF
                        buf[idx+1] = (res_c >> 8) & 0xFF

# =============================================================================
# FILE IO
# =============================================================================

def save_gip(canvas, filename):
    # Save the small buffer directly
    try:
        with open(filename, "wb") as f:
            f.write(struct.pack("<II", BUF_W, BUF_H))
            f.write(canvas.buffer)
        cgui.msgbox("Saved GIP!")
    except Exception as e:
        cgui.msgbox(f"Error: {e}")

def load_gip(canvas, filename):
    try:
        with open(filename, "rb") as f:
            w, h = struct.unpack("<II", f.read(8))
            if w != BUF_W or h != BUF_H:
                cgui.msgbox("Dim mismatch (Must be half-res)")
                return
            # Read directly into buffer, bypassing potential memoryview write issues
            f.readinto(canvas.buffer)
        canvas.draw_scaled() 
        cgui.msgbox("Loaded GIP")
    except Exception as e:
        cgui.msgbox(f"Error: {e}")

def save_bmp(canvas, filename):
    # Save the small buffer as BMP
    file_size = 14 + 40 + len(canvas.buffer)
    offset = 54
    try:
        with open(filename, "wb") as f:
            f.write(b'BM')
            f.write(struct.pack("<I", file_size))
            f.write(b'\x00\x00\x00\x00')
            f.write(struct.pack("<I", offset))
            f.write(struct.pack("<I", 40)) 
            f.write(struct.pack("<i", BUF_W))
            f.write(struct.pack("<i", -BUF_H))
            f.write(struct.pack("<H", 1))
            f.write(struct.pack("<H", 16))
            f.write(struct.pack("<I", 0))
            f.write(struct.pack("<I", len(canvas.buffer)))
            f.write(struct.pack("<ii", 2835, 2835))
            f.write(struct.pack("<II", 0, 0))
            f.write(canvas.buffer)
        cgui.msgbox("Saved BMP")
    except Exception as e:
        cgui.msgbox(f"Save Err: {e}")

# =============================================================================
# PAINT TOOLS
# =============================================================================

def draw_brush_cursor(x, y, size, color, shape='circle'):
    r = int(size // 2)
    if shape == 'circle': dcircle(x, y, r, color, color)
    elif shape == 'square': drect(x - r, y - r, x + r, y + r, color)
    elif shape == 'rect_v': drect(x - max(1, r//2), y - r, x + max(1, r//2), y + r, color)
    elif shape == 'oval': dellipse(x - r, y - max(1, r//2), x + r, y + max(1, r//2), color, color)

def bresenham(x0, y0, x1, y1):
    points = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    
    while True:
        points.append((x0, y0))
        if x0 == x1 and y0 == y1: break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy
    return points

# =============================================================================
# MAIN APP
# =============================================================================

class PaintApp:
    def __init__(self):
        self.canvas = Canvas()
        self.color = C_RGB(31, 0, 0)
        
        # Brush Props
        self.brush_size = 10
        self.brush_spacing = 5
        self.brush_spread = 0
        self.brush_flow = 100
        self.brush_opacity = 100
        self.brush_shape = 'circle'
        
        self.buttons = [
            cgui.Button(5, 5, 40, 40, "M"),
            cgui.Button(50, 5, 40, 40, "B"),
            cgui.Button(100, 5, 40, 40, "", self.color)
        ]

    def draw_toolbar(self):
        cgui.draw_panel(0, 0, SCREEN_W, HEADER_H)
        self.buttons[2].color = self.color
        for b in self.buttons:
            b.draw()
        info = f"S:{int(self.brush_size)} {self.brush_shape[:1].upper()}"
        dtext_opt(150, 25, cgui.THEME['text'], C_NONE, DTEXT_LEFT, DTEXT_MIDDLE, info, -1)

    def handle_menu(self):
        opts = ["New", "Load GIP", "Save GIP", "Save BMP", "Quit"]
        res = cinput.pick(opts, "Menu", theme='dark')
        
        if res == "New":
            self.canvas.clear(C_WHITE)
        elif res == "Save GIP":
            fn = cgui.prompt_filename(".gip")
            if fn: save_gip(self.canvas, fn)
        elif res == "Load GIP":
            fn = cgui.prompt_filename(".gip")
            if fn: load_gip(self.canvas, fn)
        elif res == "Save BMP":
            fn = cgui.prompt_filename(".bmp")
            if fn: save_bmp(self.canvas, fn)
        elif res == "Quit":
            return "QUIT"
        
        # Restore full screen logic
        clearevents()
        dtext_opt(SCREEN_W//2, SCREEN_H//2, C_WHITE, C_BLACK, DTEXT_CENTER, DTEXT_MIDDLE, "Rendering...", -1)
        dupdate()
        self.canvas.draw_scaled()
        self.draw_toolbar()
        dupdate()

    def run(self):
        self.canvas.draw_scaled()
        self.draw_toolbar()
        dupdate()
        
        last_x, last_y = -1, -1
        stroke_points = []
        painting = False
        
        while True:
            cleareventflips()
            ev = pollevent()
            events = []
            while ev.type != KEYEV_NONE:
                events.append(ev)
                ev = pollevent()

            for e in events:
                if e.type == KEYEV_TOUCH_DOWN:
                    if e.y < HEADER_H:
                        for btn in self.buttons:
                            if btn.hit(e.x, e.y):
                                btn.pressed = True
                                self.draw_toolbar()
                                dupdate()
                    else:
                        painting = True
                        last_x, last_y = e.x, e.y
                        stroke_points.append((e.x, e.y))
                        draw_brush_cursor(e.x, e.y, self.brush_size, self.color, self.brush_shape)
                        dupdate()

                elif e.type == KEYEV_TOUCH_DRAG:
                    if painting:
                        pts = bresenham(last_x, last_y, e.x, e.y)
                        for px, py in pts:
                            draw_brush_cursor(px, py, self.brush_size, self.color, self.brush_shape)
                            stroke_points.append((px, py))
                        last_x, last_y = e.x, e.y
                        dupdate()

                elif e.type == KEYEV_TOUCH_UP:
                    if painting:
                        painting = False
                        
                        dtext_opt(SCREEN_W-50, 10, C_RED, C_NONE, DTEXT_LEFT, DTEXT_TOP, "Busy", -1)
                        dupdate()
                        
                        self.canvas.bake_stroke(stroke_points, self.color, self.brush_size, 
                                              self.brush_spacing, self.brush_spread,
                                              self.brush_flow, self.brush_opacity, self.brush_shape)
                        stroke_points = []
                        
                        self.canvas.draw_scaled()
                        self.draw_toolbar()
                        dupdate()
                    
                    if self.buttons[0].pressed: # Menu
                        self.buttons[0].pressed = False
                        if self.handle_menu() == "QUIT": return

                    if self.buttons[1].pressed: # Brush
                        self.buttons[1].pressed = False
                        dlg = cgui.BrushDialog(self.brush_size, self.brush_spacing, self.brush_spread, 
                                             self.brush_flow, self.brush_opacity, self.brush_shape)
                        res = dlg.run()
                        if res:
                            self.brush_size = res['size']
                            self.brush_spacing = res['spacing']
                            self.brush_spread = res['spread']
                            self.brush_flow = res['flow']
                            self.brush_opacity = res['opacity']
                            self.brush_shape = res['shape']
                        
                        # Full redraw needed to clear dialog
                        clearevents()
                        self.canvas.draw_scaled()
                        self.draw_toolbar()
                        dupdate()
                        
                    if self.buttons[2].pressed: # Color
                        self.buttons[2].pressed = False
                        picker = cgui.ColorPicker(self.color)
                        new_col = picker.run()
                        if new_col is not None:
                            self.color = new_col
                        
                        # Full redraw needed
                        clearevents()
                        self.canvas.draw_scaled()
                        self.draw_toolbar()
                        dupdate()

            if keypressed(KEY_EXIT): return

            # Small sleep to prevent busy loop
            time.sleep(0.02)

app = PaintApp()
app.run()