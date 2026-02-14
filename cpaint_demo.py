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
        self.buffer = bytearray()
        self.mv = None
        self.clear(C_WHITE)

    def clear(self, color_int):
        hi = (color_int >> 8) & 0xFF
        lo = color_int & 0xFF
        gc.collect()
        try:
            pix = bytes([lo, hi])
            self.buffer = bytearray(pix * (BUF_W * BUF_H))
            self.mv = memoryview(self.buffer)
        except MemoryError:
            cgui.msgbox("Err: RAM full in Clear")
        dclear(color_int)

    def draw_scaled(self):
        # Full redraw from buffer
        # Can use blit_roi for full screen
        self.blit_roi(0, 0, BUF_W, BUF_H)

    def blit_roi(self, bx, by, bw, bh):
        # Draw buffer region to screen
        # bx, by, bw, bh in buffer coordinates
        if not self.mv: return
        
        cw = BUF_W
        bx = max(0, bx)
        by = max(0, by)
        bw = min(bw, BUF_W - bx)
        bh = min(bh, BUF_H - by)
        
        if bw <= 0 or bh <= 0: return

        sx = bx * 2
        sy = BUF_HEADER_OFFSET + by * 2
        
        buf = self.mv
        
        # Draw line by line to minimize function calls
        for y in range(bh):
            row_start = (by + y) * cw * 2 + (bx * 2)
            row_end = row_start + (bw * 2)
            ys = sy + y * 2
            
            ptr = row_start
            for x in range(bw):
                # Manual 2-byte read is fastest in MicroPython without struct
                lo = buf[ptr]
                hi = buf[ptr+1]
                col = (hi << 8) | lo
                ptr += 2
                
                # Draw 2x2 pixel
                drect(sx + x*2, ys, sx + x*2 + 1, ys + 1, col)

    def stroke_stamp(self, x, y, color, size, opacity, flow, shape):
        # x, y are SCREEN coordinates
        # Map to buffer coordinates
        cx = x // 2
        cy = (y - BUF_HEADER_OFFSET) // 2
        
        # Buffer dimensions
        cw, ch = BUF_W, BUF_H
        
        # Calculate radius in buffer pixels
        r_buf = max(1, int(size // 4))
        r2_buf = r_buf * r_buf
        
        # Color components
        sr, sg, sb = cgui.unpack_color(color)
        clo = color & 0xFF
        chi = (color >> 8) & 0xFF
        
        # Alpha calculation
        alpha = (opacity / 100.0) * (flow / 100.0)
        alpha = max(0.01, min(1.0, alpha))
        is_solid = (alpha >= 0.98)
        
        # Bounding box in buffer
        x_min = max(0, cx - r_buf)
        x_max = min(cw, cx + r_buf + 1)
        y_min = max(0, cy - r_buf)
        y_max = min(ch, cy + r_buf + 1)
        
        if x_min >= x_max or y_min >= y_max: return None
        
        buf = self.mv
        
        # Draw loops
        for buf_y in range(y_min, y_max):
            dy = buf_y - cy
            
            # Shape bounds optimization for row
            row_x_min, row_x_max = x_min, x_max
            
            if shape == 'circle':
                dy2 = dy*dy
                if dy2 > r2_buf: continue
                dx_limit = int(math.sqrt(r2_buf - dy2))
                row_x_min = max(x_min, cx - dx_limit)
                row_x_max = min(x_max, cx + dx_limit + 1)
            elif shape == 'rect_v':
                if abs(dy) > r_buf: continue
                dx_limit = max(1, r_buf//2)
                row_x_min = max(x_min, cx - dx_limit)
                row_x_max = min(x_max, cx + dx_limit + 1)
            elif shape == 'oval':
                if abs(dy) > max(1, r_buf//2): continue
                # circle x bounds apply roughly or full width
                # Use simplified oval (flattened circle)
                pass 

            if row_x_min >= row_x_max: continue
            
            start_idx = (buf_y * cw + row_x_min) * 2
            
            if is_solid:
                # Optimized solid fill
                # Create pattern for the row width
                # This is faster than per-pixel assignment
                width = row_x_max - row_x_min
                # buf[start_idx : start_idx + width*2] = bytes([clo, chi]) * width
                # MicroPython slice assignment might be slow for repeated creation of bytes calls?
                # Actually loop assignment is safer for memory unless we preallocate patterns.
                # For now, keep loop for safety, optimize later if needed.
                ptr = start_idx
                for _ in range(width):
                    buf[ptr] = clo
                    buf[ptr+1] = chi
                    ptr += 2
            else:
                # Blending
                ptr = start_idx
                for _ in range(row_x_max - row_x_min):
                    dlo = buf[ptr]
                    dhi = buf[ptr+1]
                    dest_c = (dhi << 8) | dlo
                    
                    # Inline unpack (RGB565 -> 5-bit)
                    dr = (dest_c >> 10) & 0x1F
                    dg = (dest_c >> 5) & 0x1F
                    db = dest_c & 0x1F
                    
                    out_r = int(sr * alpha + dr * (1.0 - alpha))
                    out_g = int(sg * alpha + dg * (1.0 - alpha))
                    out_b = int(sb * alpha + db * (1.0 - alpha))
                    
                    # Inline pack (5-bit -> RGB565)
                    res_c = ((out_r & 0x1F) << 10) | ((out_g & 0x1F) << 5) | (out_b & 0x1F)
                    
                    buf[ptr] = res_c & 0xFF
                    buf[ptr+1] = (res_c >> 8) & 0xFF
                    ptr += 2
                    
        return (x_min, y_min, x_max - x_min, y_max - y_min)

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
        self.draw_toolbar()
        
        # Initial draw
        self.canvas.draw_scaled()
        dupdate()
        
        painting = False
        last_x, last_y = 0, 0
        dist_acc = 0.0
        
        while True:
            cleareventflips()
            ev = pollevent()
            events = []
            while ev.type != KEYEV_NONE:
                events.append(ev)
                ev = pollevent()
                
            if keypressed(KEY_EXIT): return
            
            # Additional key shortcuts (Menu)
            if keypressed(KEY_KBD) or keypressed(KEY_MENU):
                import cinput
                res = cinput.pick(["Brush Settings", "Color Picker", "Fill Canvas", "Save BMP", "Quit"], "Menu")
                if res == 0:
                     dlg = cgui.BrushDialog(self.brush_size, self.brush_spacing, self.brush_spread, 
                                             self.brush_flow, self.brush_opacity, self.brush_shape)
                     val = dlg.run()
                     if val:
                         self.brush_size = val['size']
                         self.brush_spacing = val['spacing']
                         self.brush_spread = val['spread']
                         self.brush_flow = val['flow']
                         self.brush_opacity = val['opacity']
                         self.brush_shape = val['shape']
                     clearevents()
                elif res == 1:
                     picker = cgui.ColorPicker(self.color)
                     new_col = picker.run()
                     if new_col is not None:
                         self.color = new_col
                     clearevents()
                elif res == 2:
                     if cgui.ask_modal("Fill?", "Overwrite canvas?"):
                         self.canvas.clear(self.color)
                elif res == 3:
                     fname = cinput.input("Filename:", "drawing.bmp")
                     if fname: save_bmp(self.canvas, fname)
                elif res == 4: return
                
                # Draw Loading
                cgui.fill_rect(SCREEN_W//2 - 40, SCREEN_H//2 - 15, 80, 30, C_BLACK)
                dtext_opt(SCREEN_W//2, SCREEN_H//2 - 5, C_WHITE, C_NONE, DTEXT_CENTER, DTEXT_TOP, "Loading...", -1)
                dupdate()
                
                self.draw_toolbar()
                self.canvas.draw_scaled()
                dupdate()

            needs_update = False
            
            for e in events:
                if e.type == KEYEV_TOUCH_DOWN:
                    if e.y < HEADER_H:
                        for btn in self.buttons:
                            if btn.hit(e.x, e.y):
                                btn.pressed = True
                                self.draw_toolbar()
                                needs_update = True
                    else:
                        painting = True
                        last_x, last_y = e.x, e.y
                        dist_acc = 0.0
                        
                        # Apply initial stamp
                        jx = random.randint(-int(self.brush_spread), int(self.brush_spread)) if self.brush_spread > 0 else 0
                        jy = random.randint(-int(self.brush_spread), int(self.brush_spread)) if self.brush_spread > 0 else 0
                        
                        roi = self.canvas.stroke_stamp(e.x + jx, e.y + jy, self.color, self.brush_size, 
                                                     self.brush_opacity, self.brush_flow, self.brush_shape)
                        if roi:
                            self.canvas.blit_roi(*roi)
                            needs_update = True

                elif e.type == KEYEV_TOUCH_DRAG:
                    if painting:
                        # Interpolate
                        x0, y0 = last_x, last_y
                        x1, y1 = e.x, e.y
                        
                        dx = x1 - x0
                        dy = y1 - y0
                        seg_len = math.sqrt(dx*dx + dy*dy)
                        
                        if seg_len > 0:
                            dist_covered = 0.0
                            spacing = max(1.0, self.brush_spacing)
                            
                            next_step = spacing - dist_acc
                            
                            while dist_covered + next_step <= seg_len:
                                dist_covered += next_step
                                
                                t = dist_covered / seg_len
                                # Use int casting for strict coordinates as requested
                                px = int(x0 + dx * t)
                                py = int(y0 + dy * t)
                                
                                # Apply stamp
                                jx = random.randint(-int(self.brush_spread), int(self.brush_spread)) if self.brush_spread > 0 else 0
                                jy = random.randint(-int(self.brush_spread), int(self.brush_spread)) if self.brush_spread > 0 else 0
                                
                                roi = self.canvas.stroke_stamp(px + jx, py + jy, self.color, self.brush_size, 
                                                             self.brush_opacity, self.brush_flow, self.brush_shape)
                                if roi:
                                    self.canvas.blit_roi(*roi)
                                    needs_update = True
                                
                                dist_acc = 0.0
                                next_step = spacing
                                
                            dist_acc += (seg_len - dist_covered)
                        
                        last_x, last_y = e.x, e.y

                elif e.type == KEYEV_TOUCH_UP:
                    if painting:
                        painting = False
                    else:
                        redraw_needed = False
                        # Check buttons
                        if self.buttons[0].pressed: # Menu
                            self.buttons[0].pressed = False
                            # Simple Menu
                            import cinput
                            res = cinput.pick(["Fill Canvas", "Save BMP", "Quit"], "Menu")
                            print(res)
                            if res == "Fill Canvas":
                                if cgui.ask_modal("Fill?", "Overwrite canvas?"):
                                    self.canvas.clear(self.color)
                                    redraw_needed = True
                            elif res == "Save BMP":
                                fname = cinput.input("Filename:", "drawing.bmp")
                                if fname: save_bmp(self.canvas, fname)
                                redraw_needed = True
                            elif res == "Quit":
                                return
                            redraw_needed = True

                        elif self.buttons[1].pressed: # Brush
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
                            clearevents()
                            redraw_needed = True

                        elif self.buttons[2].pressed: # Color
                            self.buttons[2].pressed = False
                            picker = cgui.ColorPicker(self.color)
                            new_col = picker.run()
                            if new_col is not None:
                                self.color = new_col
                            clearevents()
                            redraw_needed = True
                        
                        if redraw_needed:
                            # Draw Loading
                            cgui.fill_rect(SCREEN_W//2 - 40 - 10, SCREEN_H//2 - 15, 80+10+10, 30, C_BLACK)
                            dtext_opt(SCREEN_W//2, SCREEN_H//2 - 5, C_WHITE, C_NONE, DTEXT_CENTER, DTEXT_TOP, "Loading...", -1)
                            dupdate()
                            self.canvas.draw_scaled()
                        
                        self.draw_toolbar()
                        needs_update = True

            if needs_update:
                dupdate()
            
            time.sleep(0.01)

app = PaintApp()
app.run()