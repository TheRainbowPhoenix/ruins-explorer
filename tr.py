from gint import *
from maze import MazeBuilder
import time
import random

# Screen configuration
dw, dh = DWIDTH, DHEIGHT
SCENE_TOP    = 0
SCENE_BOTTOM = dh // 2
UI_TOP       = SCENE_BOTTOM
UI_BOTTOM    = dh

# Vanishing point
VANISH_X = dw // 2
VANISH_Y = (SCENE_TOP + SCENE_BOTTOM) // 2

# Tunnel depth levels
LEVELS = 5
MAX_SIDE_DEPTH = 3

# seed = random.randint(0, 65535)
# print(seed)
seed = 17138

mz = MazeBuilder(10, 10, seed=seed)
grid, start, goal, key_pos, item_positions = mz.build()

MAZE_H = len(grid)
MAZE_W = len(grid[0])
maze = bytearray(sum(grid, []))

PLAYER_Y, PLAYER_X = start if start else (MAZE_H -1, MAZE_W //2)   # start at bottom row
KEY_POS = key_pos  # (y, x)
ITEM_POS = set(item_positions)  # set of (y, x) tuples

item_counter = 0 # TODO: make a class with that ? 
# 0 = looking north (–Y), 1 = east (+X), 2 = south (+Y), 3 = west (–X)
cam_dir = 0

dir_vectors = {
  0: ((-1,0),  (0,-1), (0,1)),
  1: ((0,1),   (-1,0),(1,0)),
  2: ((1,0),   (0,1), (0,-1)),
  3: ((0,-1),  (1,0), (-1,0)),
}

def lsb(data, index):
    return data[index] & 1 

def msb(data, index):
    return data[index] & 0b1000_0000 

def set_msb(data, index):
    data[index] |= 0b1000_0000   

# initialize discovery around start position
def discover(x,y):
    for dy in (-1,0,1):
        for dx in (-1,0,1):
            nx, ny = x+dx, y+dy
            if 0 <= nx < MAZE_W and 0 <= ny < MAZE_H:
                set_msb(maze, ny*MAZE_W + nx)

discover(PLAYER_X, PLAYER_Y)

# Helpers
def interp(a,b,t): return int(a+(b-a)*t)
def lerp_point(x0,y0,x1,y1,t): return (interp(x0,x1,t), interp(y0,y1,t))

def flatten(*lists):
    out = []
    for lst in lists:
        # assume each lst is itself a list of verts
        out.extend(lst)
    return out

# Draw both 3D tunnel and 2D minimap
def draw_tunnel():
    global PLAYER_X, PLAYER_Y
    # dclear(C_BLACK) # TODO: avoid this !!
    # 3D rails
    dline(0, SCENE_BOTTOM, VANISH_X, VANISH_Y, C_GREEN)
    dline(dw, SCENE_BOTTOM, VANISH_X, VANISH_Y, C_GREEN)

    fdy, fdx = dir_vectors[cam_dir][0]
    ldy, ldx = dir_vectors[cam_dir][1]
    rdy, rdx = dir_vectors[cam_dir][2]

    item_markers = []

    # compute t's
    tvals = [1.0 - 0.5**i for i in range(LEVELS+1)]
    max_shade = 30
    step = max_shade//LEVELS
    for i in range(LEVELS):
        t0,t1 = tvals[i], tvals[i+1]
        # corners near/far
        bl0 = lerp_point(0,SCENE_BOTTOM,VANISH_X,VANISH_Y,t0)
        tl0 = lerp_point(0,SCENE_TOP,   VANISH_X,VANISH_Y,t0)
        br0 = lerp_point(dw,SCENE_BOTTOM,VANISH_X,VANISH_Y,t0)
        tr0 = lerp_point(dw,SCENE_TOP,   VANISH_X,VANISH_Y,t0)
        bl1 = lerp_point(0,SCENE_BOTTOM,VANISH_X,VANISH_Y,t1)
        tl1 = lerp_point(0,SCENE_TOP,   VANISH_X,VANISH_Y,t1)
        br1 = lerp_point(dw,SCENE_BOTTOM,VANISH_X,VANISH_Y,t1)
        tr1 = lerp_point(dw,SCENE_TOP,   VANISH_X,VANISH_Y,t1)

        # shading floor/ceiling
        shade = max_shade - i*step
        floor_col = C_RGB(shade,shade,shade)
        ceil_col  = C_RGB(shade,shade,shade)
        left_open = True
        right_open = True

        # determine column and row
        # row = PLAYER_Y - i (i=0 nearest slice)
        row = PLAYER_Y - i

        # check if wall ahead
        forward_block = True
        if 0 <= row - 1 < MAZE_H and lsb(maze, (row - 1)*MAZE_W + PLAYER_X) == 1:
            forward_block = False

        if 0 <= row < MAZE_H:
            if PLAYER_X-1>=0 and lsb(maze, (row)*MAZE_W + PLAYER_X-1)==1:
                left_open = False
            if PLAYER_X+1<MAZE_W and lsb(maze, (row)*MAZE_W + PLAYER_X+1)==1:
                right_open = False
            
        # draw faces
        dpoly(flatten(bl0, br0, br1, bl1), floor_col, 1)
        dpoly(flatten(tl0,tr0,tr1,tl1), ceil_col,   1)
   

        # -------------------------
        # if there's a corridor on the left, draw the next-inner wall
        if left_open and i+1 < LEVELS:
             # compute deeper t2 and corners for sub-wall boundary
            t2 = tvals[i+2]
            bl2 = lerp_point(0, SCENE_BOTTOM, VANISH_X, VANISH_Y, t2)
            tl2 = lerp_point(0, SCENE_TOP,    VANISH_X, VANISH_Y, t2)
            # draw roof triangle (red): tl0, tl1, projected (tl0.x, tl1.y)
            x0,y0 = tl0
            x1,y1 = tl1
            dpoly([x0, y0, x1, y1, x0, y1], C_RGB(shade,shade,shade), 1)
            # draw floor triangle (red): bl0, bl1, projected (bl0.x, bl1.y)
            x0,y0 = bl0
            x1,y1 = bl1
            dpoly([x0, y0, x1, y1, x0, y1], C_RGB(shade,shade,shade), 1)
            # draw inner wall quad (orange): bl1, bl2, tl2, tl1
            dpoly([bl1[0], bl1[1], bl2[0], bl2[1], tl2[0], tl2[1], tl1[0], tl1[1]], C_RGB(31,15,0), 1)
        elif left_open:
            # if too deep, just draw flat left face
            dpoly(flatten(bl0,tl0,tl1,bl1), C_RGB(shade,shade,shade), 1)
        else:
            dpoly(flatten(bl0,tl0,tl1,bl1), C_RGB(shade,shade,shade),  1)

        # if there's a corridor on the right, draw the next-inner wall
        if right_open and i+1 < LEVELS:
            # compute t2 for deeper boundary
            t2 = tvals[i+2]
            br2 = lerp_point(dw, SCENE_BOTTOM, VANISH_X, VANISH_Y, t2)
            tr2 = lerp_point(dw, SCENE_TOP,    VANISH_X, VANISH_Y, t2)
            # check if block behind right is a wall (for coloring)
            behind_wall = False
            if 0 <= row-1 < MAZE_H and PLAYER_X+1 < MAZE_W:
                behind_wall = (lsb(maze, (row-1)*MAZE_W + (PLAYER_X+1)) == 1)
            # draw roof triangle (red) on right face: tr0, tr1, projected(tr1.x, tr0.y)
            x0, y0 = tr0
            x1, y1 = tr1
            dpoly([x0, y0, x1, y1, x0, y1], C_RGB(shade,shade,shade), 1)
            # draw floor triangle (red): br0, br1, project  ed(br1.x, br0.y)
            x0, y0 = br0
            x1, y1 = br1
            dpoly([x0, y0, x1, y1, x0, y1], C_RGB(shade,shade,shade), 1)
            # draw inner wall quad (orange or black)
            inner_col = C_RGB(31,15,0) if behind_wall else C_BLACK
            dpoly([br1[0], br1[1], br2[0], br2[1], tr2[0], tr2[1], tr1[0], tr1[1]], inner_col, 1)
        elif right_open:
            dpoly(flatten(br0,tr0,tr1,br1), C_RGB(shade,shade,shade), 1)
        else:
            dpoly(flatten(br0,tr0,tr1,br1), C_RGB(shade,shade,shade), 1)

        # -------------------------
        
        if not forward_block or i == LEVELS -1:
            # draw front-facing wall slice at the next depth and stop
            front_col = C_RGB(shade, shade, shade)
            # use the "far" corners (t1) for the wall position
            dpoly(flatten(tl1, tr1, br1, bl1), front_col, 1)
            break
        
        # draw items behind in perspective (one level)
        depth = i + 1  # next tile depth
        ty = PLAYER_Y - depth
        tx = PLAYER_X
        if depth <= LEVELS and (ty, tx) in ITEM_POS:
            t2 = tvals[depth]
            bl2 = lerp_point(0, SCENE_BOTTOM, VANISH_X, VANISH_Y, t2)
            br2 = lerp_point(dw, SCENE_BOTTOM, VANISH_X, VANISH_Y, t2)

            mx = (bl2[0] + br2[0]) // 2
            size = int(24 // (1.5**(depth)))
            my = bl1[1] - size
            item_markers.append((mx, my, size//2, depth))

            

    # back sliver
    tb = tvals[-1]
    b0 = lerp_point(0,SCENE_TOP,   VANISH_X,VANISH_Y,tb)
    b1 = lerp_point(dw,SCENE_TOP,   VANISH_X,VANISH_Y,tb)
    b2 = lerp_point(dw,SCENE_BOTTOM,VANISH_X,VANISH_Y,tb)
    b3 = lerp_point(0,SCENE_BOTTOM, VANISH_X,VANISH_Y,tb)
    # dpoly([*b0,*b1,*b2,*b3], C_RGB(10,10,10), 1)

    if (PLAYER_Y, PLAYER_X) in ITEM_POS:
        fx0, fy0 = (b0[0] + b1[0]) // 2, (b0[1] + b1[1]) // 2
        fx1, fy1 = (b2[0] + b3[0]) // 2, (b2[1] + b3[1]) // 2

        fx0 = (bl0[0] + br0[0]) // 2
        fy0 = SCENE_BOTTOM
        # back sliver floor midpoint
        fx1 = (b2[0] + b3[0]) // 2
        fy1 = (b2[1] + b3[1]) // 2
        # place at half distance
        mx = (fx0 + fx1) // 2
        my = fy0 + (fy1 - fy0) // 2
        # size of item marker
        half_w = 24
        half_h = 24
        drect(mx - half_w, my - half_h, mx + half_w, my + half_h, C_RGB(0,21,21))
        # ix0, iy0, ix1, iy1, C_RGB(0,21,21))  # cyan item marker
    
    for (mx, my, half, depth) in item_markers:
        drect(mx - half, my - half, mx + half, my + half, C_RGB(0,21-depth*2,21-depth*2))

    # UI background
    drect(0, UI_TOP, dw, UI_BOTTOM, C_RGB(2,2,2))
    # draw minimap
    cell = min((dw-20)//MAZE_W, (UI_BOTTOM-UI_TOP-20)//MAZE_H)
    mx0, my0 = 10, UI_TOP + 10
    for ry in range(MAZE_H):
        for rx in range(MAZE_W):
            idx = ry*MAZE_W + rx
            if msb(maze, idx) == 0:
                continue  # not yet discovered
            x0 = mx0 + rx*cell
            y0 = my0 + ry*cell
            # wall = black, corridor = white
            col = C_WHITE if lsb(maze, idx) == 0 else C_BLACK
            drect(x0, y0, x0+cell, y0+cell, col)
            # draw key if at this cell
            if lsb(maze, idx) == 0:
                if (ry, rx) == KEY_POS:
                    drect(x0+2, y0+2, x0+cell-2, y0+cell-2, C_RGB(21,21,0))  # yellow key square
                # draw items if any at this cell
                if (ry, rx) in ITEM_POS:
                    drect(x0+cell//4, y0+cell//4, x0+3*cell//4, y0+3*cell//4, C_RGB(0,21,21))  # cyan
    
    # draw player arrow based on orientation
    px = mx0 + PLAYER_X*cell + cell//2
    py = my0 + PLAYER_Y*cell + cell//2
    dx, dy = dir_vectors[cam_dir][1]
    pdx, pdy = -dy, dx
    dpoly([
        px + dx*cell//2,       py + dy*cell//2,  # tip
        px - pdx*cell//4,      py - pdy*cell//4,   # base left
        px + pdx*cell//4,      py + pdy*cell//4,   # base right
    ], C_RED, 1)

    # player dot
    # px = mx0 + PLAYER_X*cell + cell//4
    # py = my0 + PLAYER_Y*cell + cell//4
    # drect(px, py, px+cell//2, py+cell//2, C_RED)

    # px = mx0 + PLAYER_X*cell + cell//4
    # py = my0 + PLAYER_Y*cell + cell//4
    # drect(px, py, px+cell//2, py+cell//2, C_RED)

    # UI text
    dtext(5, UI_TOP+5, C_WHITE, "[UP/DOWN/LEFT/RIGHT] Move   [EXE] Interact")
    dupdate()

# Main loop

draw_tunnel()
while True:
    ev = pollevent()
    if ev.type == KEYEV_DOWN:
        if ev.key == KEY_EXIT:
            break
        elif ev.key == KEY_UP:
            ny, nx = PLAYER_Y - 1, PLAYER_X
            if ny >= 0 and lsb(maze, ny*MAZE_W+nx) == 0:
                PLAYER_Y = ny
                discover(PLAYER_X, PLAYER_Y)
        elif ev.key == KEY_DOWN:
            ny, nx = PLAYER_Y + 1, PLAYER_X
            if ny < MAZE_H and lsb(maze, ny*MAZE_W+nx) == 0:
                PLAYER_Y = ny
                discover(PLAYER_X, PLAYER_Y)
        elif ev.key == KEY_LEFT:
            nx, ny = PLAYER_X - 1, PLAYER_Y
            if nx >= 0 and lsb(maze, ny*MAZE_W+nx) == 0:
                PLAYER_X = nx
                discover(PLAYER_X, PLAYER_Y)
        elif ev.key == KEY_RIGHT:
            nx, ny = PLAYER_X + 1, PLAYER_Y
            if nx < MAZE_W and lsb(maze, ny*MAZE_W+nx) == 0:
                PLAYER_X = nx
                discover(PLAYER_X, PLAYER_Y)
        elif ev.key == KEY_EXE:
            # pick up item if present
            pos = (PLAYER_Y, PLAYER_X)
            if pos in ITEM_POS:
                ITEM_POS.remove(pos)
                item_counter += 1
                dtext(5, UI_TOP+25, C_WHITE, f"Items: {item_counter}")
                # dupdate() -let draw_tunnel call it
        elif ev.key == KEY_SHIFT:
            cam_dir = (cam_dir + 1) % 4
            # draw_tunnel() -let draw_tunnel parent
        # redraw after move
        draw_tunnel()
    time.sleep(0.05)
