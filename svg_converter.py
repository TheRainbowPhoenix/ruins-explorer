from svg_vector_format import VectorCompiler, BIN_C_NONE
from gint import C_RGB, C_BLACK, C_WHITE, C_NONE
import math

#  INPUT ASSETS
# Add your SVG paths here
ASSETS = {
    "SHUFFLE": "M19.28 16.34L17.46 15s.32-.59.96-1.78a.944.944 0 0 1 1.6 0l.81 1.26c.19.3.21.68.06 1l-.22.47a.94.94 0 0 1-1.39.39m-14.56 0a.946.946 0 0 1-1.39-.38l-.23-.47c-.15-.32-.13-.7.06-1l.81-1.26a.944.944 0 0 1 1.6 0c.65 1.18.97 1.77.97 1.77zm10.64-6.97c.09-.68.73-1.06 1.27-.75l1.59.9c.46.26.63.91.36 1.41L16.5 15h-1.8zm-6.73 0L9.3 15H7.5l-2.09-4.08c-.27-.5-.1-1.15.36-1.41l1.59-.9c.53-.3 1.18.08 1.27.76M13.8 15h-3.6l-.74-6.88c-.07-.59.35-1.12.88-1.12h3.3c.53 0 .94.53.88 1.12z",
    "CROP": "M21.25 10.5c-.41 0-.75.34-.75.75h-1.54a7 7 0 0 0-1.52-3.65l1.09-1.09l.01.01c.29.29.77.29 1.06 0s.29-.77 0-1.06L18.54 4.4a.754.754 0 0 0-1.06 0c-.29.29-.29.76-.01 1.05l-1.09 1.09a7 7 0 0 0-3.64-1.51V3.5h.01c.41 0 .75-.34.75-.75S13.16 2 12.75 2h-1.5c-.41 0-.75.34-.75.75s.33.74.74.75v1.55c-1.37.14-2.62.69-3.64 1.51L6.51 5.47l.01-.01c.29-.29.29-.77 0-1.06a.754.754 0 0 0-1.06 0L4.4 5.46c-.29.29-.29.77 0 1.06s.76.29 1.05.01l1.09 1.09a6.9 6.9 0 0 0-1.5 3.63H3.5c0-.41-.34-.75-.75-.75s-.75.34-.75.75v1.5c0 .41.34.75.75.75s.75-.34.75-.75h1.54c.15 1.37.69 2.61 1.5 3.63l-1.09 1.09a.74.74 0 0 0-1.05.01c-.29.29-.29.77 0 1.06l1.06 1.06c.29.29.77.29 1.06 0s.29-.77 0-1.06l-.01-.01l1.09-1.09c1.02.82 2.26 1.36 3.63 1.51v1.55c-.41.01-.74.34-.74.75s.34.75.75.75h1.5c.41 0 .75-.34.75-.75s-.34-.75-.75-.75h-.01v-1.54c1.37-.14 2.62-.69 3.64-1.51l1.09 1.09c-.29.29-.28.76.01 1.05s.77.29 1.06 0l1.06-1.06c.29-.29.29-.77 0-1.06a.754.754 0 0 0-1.06 0l-.01.01l-1.09-1.09a7.03 7.03 0 0 0 1.52-3.65h1.54c0 .41.34.75.75.75s.75-.34.75-.75v-1.5c.01-.4-.33-.74-.74-.74M13.75 8c.55 0 1 .45 1 1s-.45 1-1 1s-1-.45-1-1s.45-1 1-1M12 13c-.55 0-1-.45-1-1s.45-1 1-1s1 .45 1 1s-.45 1-1 1m-1.75-5c.55 0 1 .45 1 1s-.45 1-1 1s-1-.45-1-1s.45-1 1-1M8.5 13c-.55 0-1-.45-1-1s.45-1 1-1s1 .45 1 1s-.45 1-1 1m1.75 3c-.55 0-1-.45-1-1s.45-1 1-1s1 .45 1 1s-.45 1-1 1m3.5 0c-.55 0-1-.45-1-1s.45-1 1-1s1 .45 1 1s-.45 1-1 1m.75-4c0-.55.45-1 1-1s1 .45 1 1s-.45 1-1 1s-1-.45-1-1",
    "DEVICE": "M12.95 19H20V7H4v12h7.24c.14-.98.42-2.05-.16-2.43c-.89-.59-1.27 2.06-2.8 1.35c-1.39-1.12 1.05-1.29.5-3.27c-.22-.79-2.28.36-2.4-1.24c-.08-1 1.49-.74 1.51-1.49c.03-.75-1.03-1.05-.25-1.91c.22-.24.71-.26.91-.19c.79.27 1.55 1.82 2.51 1.19c1.03-.66-1.88-2.35 0-2.86c1.64-.44 1.31 2.08 2.65 2.44c1.94.52 2.65-4.55 4.41-2.33c1.85 2.33-3.43 2.27-2.85 4.01c.34 1.01 2.15-1.2 2.76.53c.64 1.83-3.09.82-3.04 1.66c.06.83 2.41.55 1.64 2.12c-1.14 1.86-3-1.03-3.81.09c-.39.57-.09 1.49.13 2.33M20 5c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V7c0-1.1.9-2 2-2h3.17L9 3h6l1.83 2zm-1.86 13.01c-.47 0-.86-.38-.86-.86s.38-.86.86-.86c.47 0 .86.38.86.86s-.38.86-.86.86",
    "TREBLE": "M29 14v8l-4 10-5 5 2 9h5l5 2 5 5 1 8-1 6-4 5-6 2 3 15-3 6-8 4-5-2-4-5v-3l3-5 4-1 4 3 1 5-4 4h-4l2 1 3 1 7-3 2-5-3-14H15l-7-4-6-8-1-10 9-15 7-7-2-8v-9l4-11 5-3Zm-5-7-4 4-3 11 1 8 5-5 4-11Zm-6 32L8 50 5 60l3 7 7 6h10l-4-21-6 3-2 6 3 6 6 4h-2l-5-3-4-5v-6l2-6 7-5Zm5 13 4 20 5-2 3-6-2-7-5-5Z"
}

#  PARSING LOGIC (Optimized)

def tokenize_svg(path):
    tokens = []
    i = 0
    length = len(path)
    while i < length:
        char = path[i]
        if char.isalpha():
            tokens.append(char)
            i += 1
        elif char.isspace() or char == ",":
            i += 1
        else:
            start = i
            if char == "-": i += 1
            has_dot = False
            while i < length:
                c = path[i]
                if c.isdigit(): i += 1
                elif c == ".":
                    if has_dot: break
                    has_dot = True
                    i += 1
                else: break
            if i > start: tokens.append(path[start:i])
            else: i += 1
    return tokens

def point_on_cubic_bezier(p0, p1, p2, p3, t):
    x = (1-t)**3 * p0[0] + 3*(1-t)**2 * t * p1[0] + 3*(1-t) * t**2 * p2[0] + t**3 * p3[0]
    y = (1-t)**3 * p0[1] + 3*(1-t)**2 * t * p1[1] + 3*(1-t) * t**2 * p2[1] + t**3 * p3[1]
    return x, y

def sample_bezier(p0, p1, p2, p3, segments=3): # Reduced segments for baked efficiency
    pts = []
    for i in range(1, segments + 1):
        pts.extend(point_on_cubic_bezier(p0, p1, p2, p3, i / segments))
    return pts

def arc_to_beziers(px, py, rx, ry, rot, large, sweep, x, y):
    # Simplified approximation suitable for icons
    mid_x = (px + x) / 2 + (x - px) * 0.2
    mid_y = (py + y) / 2 + (y - py) * 0.2
    return [mid_x, mid_y, x, y]

def parse_svg_to_polys(path_str):
    tokens = tokenize_svg(path_str)
    polys = []
    current_poly = []
    cx, cy = 0.0, 0.0
    start_x, start_y = 0.0, 0.0
    idx = 0
    last_cmd = None
    last_ctrl_x, last_ctrl_y = 0.0, 0.0
    
    while idx < len(tokens):
        token = tokens[idx]
        cmd = token if token[0].isalpha() else (last_cmd if last_cmd in 'MLHVCCSQTAZ' else ('L' if last_cmd=='M' else ('l' if last_cmd=='m' else last_cmd)))
        if token[0].isalpha(): idx += 1
        last_cmd = cmd
        
        if cmd not in ['C','c','S','s']: last_ctrl_x, last_ctrl_y = cx, cy

        if cmd in ['M', 'L', 'H', 'V', 'Z', 'm', 'l', 'h', 'v', 'z']:
            # Linear Commands
            if cmd=='M': cx=float(tokens[idx]); idx+=1; cy=float(tokens[idx]); idx+=1; start_x,start_y=cx,cy; 
            elif cmd=='m': cx+=float(tokens[idx]); idx+=1; cy+=float(tokens[idx]); idx+=1; start_x,start_y=cx,cy; 
            elif cmd=='L': cx=float(tokens[idx]); idx+=1; cy=float(tokens[idx]); idx+=1
            elif cmd=='l': cx+=float(tokens[idx]); idx+=1; cy+=float(tokens[idx]); idx+=1
            elif cmd=='H': cx=float(tokens[idx]); idx+=1
            elif cmd=='h': cx+=float(tokens[idx]); idx+=1
            elif cmd=='V': cy=float(tokens[idx]); idx+=1
            elif cmd=='v': cy+=float(tokens[idx]); idx+=1
            elif cmd in ['Z','z']: 
                if abs(cx-start_x)>0.1 or abs(cy-start_y)>0.1: current_poly.extend([start_x, start_y])
                if current_poly: polys.append(current_poly); current_poly=[]
                cx, cy = start_x, start_y
                continue
            
            if cmd in ['M','m'] and len(current_poly) > 2: polys.append(current_poly[:-2]); current_poly=[cx,cy]
            elif cmd in ['M','m']: current_poly=[cx,cy]
            else: current_poly.extend([cx, cy])
            
        elif cmd in ['C', 'c', 'S', 's']:
            # Cubic Beziers
            if cmd in ['C', 'c']:
                x1 = float(tokens[idx]) + (0 if cmd=='C' else cx); idx+=1
                y1 = float(tokens[idx]) + (0 if cmd=='C' else cy); idx+=1
                x2 = float(tokens[idx]) + (0 if cmd=='C' else cx); idx+=1
                y2 = float(tokens[idx]) + (0 if cmd=='C' else cy); idx+=1
                tx = float(tokens[idx]) + (0 if cmd=='C' else cx); idx+=1
                ty = float(tokens[idx]) + (0 if cmd=='C' else cy); idx+=1
                p1, p2 = (x1, y1), (x2, y2)
            else: # S/s
                x2 = float(tokens[idx]) + (0 if cmd=='S' else cx); idx+=1
                y2 = float(tokens[idx]) + (0 if cmd=='S' else cy); idx+=1
                tx = float(tokens[idx]) + (0 if cmd=='S' else cx); idx+=1
                ty = float(tokens[idx]) + (0 if cmd=='S' else cy); idx+=1
                p1 = (cx + (cx - last_ctrl_x), cy + (cy - last_ctrl_y))
                p2 = (x2, y2)
                
            current_poly.extend(sample_bezier((cx,cy), p1, p2, (tx,ty)))
            cx, cy = tx, ty
            last_ctrl_x, last_ctrl_y = p2[0], p2[1]

        elif cmd == 'a':
            rx=float(tokens[idx]); idx+=2; rot=float(tokens[idx]); idx+=3 # skip ry, large, sweep for now
            dx=float(tokens[idx]); idx+=1; dy=float(tokens[idx]); idx+=1
            dest_x, dest_y = cx+dx, cy+dy
            current_poly.extend(arc_to_beziers(cx, cy, rx, rx, rot, 0, 0, dest_x, dest_y))
            cx, cy = dest_x, dest_y

    if current_poly: polys.append(current_poly)
    return polys

#  GEOMETRY & BRIDGING

def ccw(A, B, C):
    return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])

def segments_intersect(p1, p2, p3, p4):
    if p1 == p3 or p1 == p4 or p2 == p3 or p2 == p4: return False
    return ccw(p1,p3,p4) != ccw(p2,p3,p4) and ccw(p1,p2,p3) != ccw(p1,p2,p4)

def is_point_in_poly(x, y, poly_pts, bbox):
    min_x, min_y, max_x, max_y = bbox
    if x < min_x or x > max_x or y < min_y or y > max_y: return False
    n = len(poly_pts); inside = False; p1x, p1y = poly_pts[0]
    for i in range(n + 1):
        p2x, p2y = poly_pts[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y: xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters: inside = not inside
        p1x, p1y = p2x, p2y
    return inside

def merge_polys_with_holes(raw_polys):
    if not raw_polys: return []
    if len(raw_polys) == 1: return raw_polys[0]

    polys_pts = [[(rp[k], rp[k+1]) for k in range(0, len(rp), 2)] for rp in raw_polys]
    main_poly = polys_pts[0]
    holes = polys_pts[1:]
    
    xs = [p[0] for p in main_poly]; ys = [p[1] for p in main_poly]
    bbox = (min(xs), min(ys), max(xs), max(ys))

    for hole in holes:
        if not hole: continue
        candidates = []
        for i, m_pt in enumerate(main_poly):
            for j, h_pt in enumerate(hole):
                candidates.append( ((m_pt[0]-h_pt[0])**2 + (m_pt[1]-h_pt[1])**2, i, j) )
        candidates.sort(key=lambda x: x[0])
        
        best_m, best_h = 0, 0
        for dist, i, j in candidates[:25]: # Check top 25 closest
            m_pt, h_pt = main_poly[i], hole[j]
            mid_x, mid_y = (m_pt[0] + h_pt[0]) / 2, (m_pt[1] + h_pt[1]) / 2
            if not is_point_in_poly(mid_x, mid_y, main_poly, bbox): continue
            
            intersect = False
            for k in range(len(main_poly)):
                if segments_intersect(m_pt, h_pt, main_poly[k], main_poly[(k+1)%len(main_poly)]):
                    intersect = True; break
            if not intersect:
                best_m, best_h = i, j; break
        
        rotated_hole = hole[best_h:] + hole[:best_h]
        main_poly = main_poly[:best_m+1] + rotated_hole + [rotated_hole[0]] + main_poly[best_m:]

    return [c for pt in main_poly for c in pt]

#  EXPORT

def generate_file():
    print("Compiling Assets...")
    
    # 1. Text-based Python List Format
    print("- Generating svg_generated_icons.py...")
    output_py = []
    output_py.append("# Auto-generated icons. Format: Fixed-point integers (Scale x100)")
    output_py.append("# Usage: real_x = (pt * scale) // 100 + x")
    output_py.append("")
    
    # 2. Binary Format (using vector_format logic)
    print("- Generating icons_bin.py...")
    
    # We will generate a dictionary where each key maps to a distinct binary blob
    binary_dict = {}
    # compiler = VectorCompiler()
    
    for name, path in ASSETS.items():
        print(f"  Processing {name}...")
        raw = parse_svg_to_polys(path)
        merged = merge_polys_with_holes(raw)
        
        # Scale by 100 and convert to Int for Python list
        fixed_poly = [int(val * 100) for val in merged]
        output_py.append(f"{name} = {fixed_poly}")
        
        # Binary Compilation
        # Create a new compiler for each icon so they are separate blobs
        compiler = VectorCompiler()
        # Assume black fill for simplicity in auto-conversion
        compiler.add_poly(fixed_poly, C_BLACK, BIN_C_NONE)
        binary_dict[name] = compiler.get_bytes()

    # Save Text Format
    with open("svg_generated_icons.py", "w") as f:
        f.write("\n".join(output_py))
        
    # Save Binary Format (Dictionary)
    # bin_data = compiler.get_bytes()
    with open("icons_bin.py", "w") as f:
        f.write("# Binary data container\n")
        f.write("# keys: Icon Name, values: Binary Blob (bytes)\n")
        f.write("ICONS_BINARY = {\n")
        for k, v in binary_dict.items():
            f.write(f"    '{k}': {v},\n")
        f.write("}\n")
    
    print("Done! 'svg_generated_icons.py' and 'icons_bin.py' created.")

if __name__ == "__main__":
    generate_file()