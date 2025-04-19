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


seed = random.randint(0, 65535)
print(seed)
seed = 17138

mz = MazeBuilder(10, 10, seed=seed)
grid, start, goal = mz.build()

MAZE_H = len(grid)
MAZE_W = len(grid[0])
maze = bytearray(sum(grid, []))

PLAYER_Y, PLAYER_X = start   # start at bottom row


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

# Draw both 3D tunnel and 2D minimap
def draw_tunnel():
    global PLAYER_X, PLAYER_Y
    dclear(C_BLACK)
    # 3D rails
    dline(0, SCENE_BOTTOM, VANISH_X, VANISH_Y, C_GREEN)
    dline(dw, SCENE_BOTTOM, VANISH_X, VANISH_Y, C_GREEN)

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
        dpoly([*bl0,*br0,*br1,*bl1], floor_col, 1)
        dpoly([*tl0,*tr0,*tr1,*tl1], ceil_col,   1)
   

        # -------------------------
        # if there's a corridor on the left, draw the next-inner wall
        if left_open:
            if  i+1 < LEVELS:
                t2 = tvals[i+2]
                # compute deeper corners
                bl2 = lerp_point(0, SCENE_BOTTOM, VANISH_X, VANISH_Y, t2)
                tl2 = lerp_point(0, SCENE_TOP,    VANISH_X, VANISH_Y, t2)
                shade2 = max(shade - step, 0)
                inner_col = C_RGB(shade2, shade2, shade2)
                # draw sub-wall on left face
                dpoly([*bl1, *bl2, *tl2, *tl1], inner_col, 1)
            else:
                dpoly([*bl0,*tl0,*tl1,*bl1], C_RGB(4,0,12),  1)
        else:
            dpoly([*bl0,*tl0,*tl1,*bl1], C_RGB(shade,shade,shade),  1)

        # if open :  
        
        # if there's a corridor on the right, draw the next-inner wall
        if right_open:
            if i+1 < LEVELS:
                t2 = tvals[i+2]
                # compute deeper corners
                br2 = lerp_point(dw, SCENE_BOTTOM, VANISH_X, VANISH_Y, t2)
                tr2 = lerp_point(dw, SCENE_TOP,    VANISH_X, VANISH_Y, t2)
                shade2 = max(shade - step, 0)
                inner_col = C_RGB(shade2, shade2, shade2)
                # draw sub-wall on right face
                dpoly([*br1, *br2, *tr2, *tr1], inner_col, 1)
            else:
                dpoly([*br1, *br2, *tr2, *tr1], C_RGB(4,0,12), 1)
        else:
            dpoly([*br0,*tr0,*tr1,*br1], C_RGB(shade,shade,shade), 1)

        # -------------------------
        
        if not forward_block:
            # draw front-facing wall slice at the next depth and stop
            front_col = C_RGB(shade, shade, shade)
            # use the "far" corners (t1) for the wall position
            dpoly([*tl1, *tr1, *br1, *bl1], front_col, 1)
            break
    # back sliver
    tb = tvals[-1]
    b0 = lerp_point(0,SCENE_TOP,   VANISH_X,VANISH_Y,tb)
    b1 = lerp_point(dw,SCENE_TOP,   VANISH_X,VANISH_Y,tb)
    b2 = lerp_point(dw,SCENE_BOTTOM,VANISH_X,VANISH_Y,tb)
    b3 = lerp_point(0,SCENE_BOTTOM, VANISH_X,VANISH_Y,tb)
    # dpoly([*b0,*b1,*b2,*b3], C_RGB(10,10,10), 1)

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
    # player dot
    px = mx0 + PLAYER_X*cell + cell//4
    py = my0 + PLAYER_Y*cell + cell//4
    drect(px, py, px+cell//2, py+cell//2, C_RED)

    px = mx0 + PLAYER_X*cell + cell//4
    py = my0 + PLAYER_Y*cell + cell//4
    drect(px, py, px+cell//2, py+cell//2, C_RED)

    # UI text
    dtext(5, UI_TOP+5, C_WHITE, "[UP/DOWN/LEFT/RIGHT] Move   [EXE] Interact")
    dupdate()

# Main loop
if __name__=='__main__':
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
            # redraw after move
            draw_tunnel()
        time.sleep(0.05)
