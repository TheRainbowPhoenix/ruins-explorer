from gint import *
from maze import MazeBuilder
import time
import struct
import random
from gui_old import gui_bg

CLEAR_COLOR     = C_RGB(31,31,31)

SCREEN_W     = DWIDTH
SCREEN_H     = DHEIGHT

# --- Helpers ---

def lsb(data, index):
    return data[index] & 1 

def msb(data, index):
    return data[index] & 0b1000_0000 

def set_msb(data, index):
    data[index] |= 0b1000_0000   

def interp(a,b,t): return int(a+(b-a)*t)
def lerp_point(x0,y0,x1,y1,t): return (interp(x0,x1,t), interp(y0,y1,t))

def flatten(*lists):
    out = []
    for lst in lists:
        out.extend(lst)
    return out

# --- Camera ---
class Camera:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

# --- Enemies ---
class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.last_move = time.monotonic()

# --- Scene Base ---
class Scene:
    def __init__(self):
        self.camera = Camera()
        self.running = False

    def preload(self): pass
    def create(self): pass
    def update(self, t, dt): pass

# --- Start Scene ---
class StartScene(Scene):
    def __init__(self):
        super().__init__()
        self.options = ["Start Game", "Free Play", "Random Seed", "Custom Seed...", "Exit Game"]
        self.selected = 0
        self.input_mode = False
        self.seed_input = ""
        self.generated_seed = random.randint(0, 99999)

    def create(self):
        dclear(C_RGB(1, 5, 6))
        dtext(60, 60, C_RGB(6,15,15), "Temple of the")
        dtext(60, 80, C_RGB(6,15,15), "Spiral Serpent")
        for i, option in enumerate(self.options):
            color = C_RGB(6,15,15) if i == self.selected else C_WHITE
            dtext(60, DHEIGHT//2 + i * 15, color, option)
        dtext(60, DHEIGHT//2 + len(self.options) * 15 + 5, C_WHITE, f"Seed: {self.generated_seed if not self.input_mode else self.seed_input}")
        dupdate()

    keys_map = {
        KEY_0: "0",
        KEY_1: "1",
        KEY_2: "2",
        KEY_3: "3",
        KEY_4: "4",
        KEY_5: "5",
        KEY_6: "6",
        KEY_7: "7",
        KEY_8: "8",
        KEY_9: "9",
    }

    def update(self, t, dt):
        ev = pollevent()
        if self.input_mode:
            if ev.type == KEYEV_DOWN:
                if len(self.seed_input) < 5:
                    k = self.keys_map.get(ev.key, None)
                    if k:
                        self.seed_input += k
                elif ev.key == KEY_DEL and self.seed_input:
                    self.seed_input = self.seed_input[:-1]
                elif ev.key in [KEY_EXE, KEY_UP]:
                    if self.seed_input:
                        seed = int(self.seed_input)
                        return TunnelScene(seed)
                elif ev.key == KEY_EXIT:
                    self.input_mode = False
                    # self.seed_input = ""
                self.create()
        else:
            if ev.type == KEYEV_DOWN:
                if ev.key == KEY_UP:
                    self.selected = (self.selected - 1) % len(self.options)
                    self.create()
                elif ev.key == KEY_DOWN:
                    self.selected = (self.selected + 1) % len(self.options)
                    self.create()
                elif ev.key == KEY_EXE:
                    if self.selected == 0:
                        # Start Game: play intro cinematic first
                        return IntroScene(self.generated_seed)
                    elif self.selected == 1: # Free Play: skip intro, go straight to gameplay
                        return TunnelScene(self.generated_seed)
                    elif self.selected == 2:
                        self.generated_seed = random.randint(0, 99999)
                        self.create()
                    elif self.selected == 3:
                        self.input_mode = True
                        self.seed_input = ""
                        self.create()
                    elif self.selected == 4: # Exit
                        exit()
                
                elif ev.key == KEY_EXIT:
                    exit()
        return None

# --- IntroScene ---
class IntroScene(Scene):
    def __init__(self, seed=None):
        super().__init__()
        self.page = 0
        self.seed = seed
        # ≤ ~24 chars per line for 320px width
        self.pages = [
            [
                "WELCOME TO SPIRAL SERPENT",
                "",
                "Long ago, the Spiral Serpent hid",
                "its power in Relic Runes.",
                "It sealed them in the shifting",
                "halls of the Temple of the",
                "Spiral Serpent.",
                "Many have tried… all have failed.",
                "",
                "Press [ENTER] to continue"
            ],
            [
                "JUNGLE OF XUL'KARA",
                "",
                "In the heart of Xul'Kara's emerald",
                "canopy, ancient ruins lie hidden",
                "beneath vines. Forgotten altars",
                "echo with distant chants,",
                "and shadows shift as if alive.",
                "Hints of serpent glyphs glimmer",
                "on stones, drawing explorers",
                "deeper into peril. Twisting paths",
                "lead to the temple gates.",
                "",
                "Press [ENTER] to continue"
            ],
            [
                "YOUR MISSION",
                "",
                "You are Dr. John Hawkstone,",
                "archaeologist and relic hunter.",
                "",
                " - Explore maze halls",
                " - Recover all 10 Relic Runes",
                " - Beat roaming sentries",
                "",
                "CONTROLS",
                "",
                " - MOVE: Arrow keys",
                " - EXAMINE: EXE",
                "",
                "Press [ENTER] to enter temple"
            ]
        ]
        # time when current page started revealing
        self.start = time.monotonic()
        # reveal one line every 0.8s
        self.interval = 0.6

    def draw_text(self, t, dt):
        dclear(C_RGB(1, 5, 6))            # dark teal background
        text_color = C_RGB(6, 15, 15)     # bright teal text
        x, y, lh = 20, 40, 18

        elapsed = t - self.start
        # how many lines to show so far
        lines_to_show = int(elapsed / self.interval) + 1
        lines_to_show = min(lines_to_show, len(self.pages[self.page]))

        for i in range(lines_to_show):
            dtext(x, y + i*lh, text_color, self.pages[self.page][i])
        dupdate()

    def update(self, t, dt):
        # always draw current reveal state
        self.draw_text(t, dt)

        # compute if current page is fully revealed
        elapsed = t - self.start
        total_lines = len(self.pages[self.page])
        fully_revealed = elapsed >= (total_lines - 1) * self.interval

        ev = pollevent()
        if ev.type == KEYEV_DOWN:
            if ev.key == KEY_EXE and fully_revealed:
                self.page += 1
                if self.page >= len(self.pages):
                    # all pages shown → start game
                    return TunnelScene(self.seed or random.randint(0,99999))
                # reset reveal timer for new page
                self.start = t
            elif ev.key == KEY_EXIT:
                exit()

        return None





# --- Tunnel Scene ---
class TunnelScene(Scene):
    def __init__(self, seed = None): # type: (int |None) -> None
        super().__init__()
        if not seed:
            seed = random.randint(0, 65535) # 17138
        self.max_items = 10
        self.generate_dungeon(seed)
        self.item_counter = 0
        self.total_score = 0

        self.dir_vectors = {
          0: ((-1,0),(0,-1),(0,1)),
          1: ((0,1),(-1,0),(1,0)),
          2: ((1,0),(0,1),(0,-1)),
          3: ((0,-1),(1,0),(-1,0)),
        }
        
        self.COLORS_MAP = [
            [ C_RGB(10, 18, 17), C_RGB(5, 15, 15), C_RGB(2, 9, 10) ], # 0: Walls, floor, roof
            [ C_RGB(6, 11, 10), C_RGB(3, 9, 9), C_RGB(1, 7, 8) ], # 1: Walls, floor, roof
            [ C_RGB(4, 7, 6), C_RGB(2, 6, 6), C_RGB(1, 4, 5) ], # 2: Walls, floor, roof
            [ C_RGB(2, 4, 3), C_RGB(1, 3, 3), C_RGB(1, 3, 4) ], # 3: Walls, floor, roof
            [ C_RGB(1, 2, 2), C_RGB(1, 2, 2), C_RGB(0, 2, 3) ], # 4: Walls, floor, roof
            [ C_RGB(0, 1, 1), C_RGB(0, 1, 1), C_RGB(0, 1, 2) ], # 5: Walls, floor, roof
            [ C_RGB(0, 1, 1), C_RGB(0, 1, 1), C_RGB(0, 1, 2) ], # 5: Walls, floor, roof

            # [ C_RGB(19, 13, 1), C_RGB(19, 13, 2), C_RGB(16, 10, 1) ], # 0: Walls, floor, roof
            # [ C_RGB(13, 8, 0), C_RGB(14, 10, 3), C_RGB(13, 8, 1) ], # 1: Walls, floor, roof
            # [ C_RGB(12, 8, 1), C_RGB(13, 9, 3), C_RGB(12, 7, 1) ], # 2: Walls, floor, roof
            # [ C_RGB(12, 7, 1), C_RGB(12, 7, 1), C_RGB(11, 7, 1) ], # 3: Walls, floor, roof
            # [ C_RGB(10, 6, 0), C_RGB(10, 6, 0), C_RGB(9, 7, 0) ], # 4: Walls, floor, roof
        ]
        self.BG_COLOR = C_RGB(10, 6, 1)


    def generate_dungeon(self, seed):
        mz = MazeBuilder(15, 10, seed=seed, items_count=self.max_items, enemies_count=2)
        grid, start, goal, key_pos, items, enemies_pos = mz.build()
        self.MAZE_H = len(grid)
        self.MAZE_W = len(grid[0])
        self.GOAL = goal
        self.maze = bytearray(sum(grid, []))
        self.PLAYER_Y, self.PLAYER_X = start if start else (self.MAZE_H-1, self.MAZE_W//2)
        self.KEY_POS = key_pos
        self.ITEM_POS = set(items)
        self.cam_dir = 0  # 0=N,1=E,2=S,3=W
        self.item_counter = 0
        self.enemies = [Enemy(x, y) for (y, x) in enemies_pos]
        self.enemy_move_interval = 2
        self.discover_radius()

    def discover_radius(self):
        # reveal 3x3 around player
        for dy in (-1,0,1):
            for dx in (-1,0,1):
                nx, ny = self.PLAYER_X+dx, self.PLAYER_Y+dy
                if 0<=nx<self.MAZE_W and 0<=ny<self.MAZE_H:
                    idx = ny*self.MAZE_W+nx
                    self.maze[idx] |= 0b10000000

    def preload(self):
        pass

    def create(self):
        # initial draw
        self.draw_tunnel()
        self.draw_gui_base()
        self.draw_gui_map()
        self.draw_gui_text()
        dupdate()

    def redraw_scene_only(self):
        self.draw_tunnel()
        self.draw_gui_map(clean=True)
        self.draw_gui_text(clean=True)
        dupdate()

    def update(self, now, dt):
        ev = pollevent()
        if ev.type == KEYEV_DOWN:
            # movement
            if ev.key == KEY_EXIT:
                return "POP"
            # if ev.key == KEY_EQUALS:
            #     return MenuScene()
            
            if ev.key in (KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT):
                dy, dx = 0, 0
                if ev.key == KEY_UP:    dy,dx = -1,0
                if ev.key == KEY_DOWN:  dy,dx = 1,0
                if ev.key == KEY_LEFT:  dy,dx = 0,-1
                if ev.key == KEY_RIGHT: dy,dx = 0,1
                ny = self.PLAYER_Y + dy
                nx = self.PLAYER_X + dx
                idx = ny*self.MAZE_W+nx
                if 0<=nx<self.MAZE_W and 0<=ny<self.MAZE_H and (self.maze[idx]&1)==0:
                    self.PLAYER_X, self.PLAYER_Y = nx, ny
                    self.discover_radius()
            elif ev.key == KEY_SHIFT:
                self.cam_dir = (self.cam_dir + 1) % 4
            elif ev.key == KEY_EXE:
                pos = (self.PLAYER_Y, self.PLAYER_X)
                if pos in self.ITEM_POS:
                    self.ITEM_POS.remove(pos)
                    self.item_counter += 1
                elif (self.PLAYER_Y, self.PLAYER_X ) == self.KEY_POS:
                    self.KEY_POS = None
                    self.total_score += 5
                for e in self.enemies:
                    if e.x == self.PLAYER_X and e.y == self.PLAYER_Y:
                        self.enemies.remove(e)
                        self.total_score += 2
                        break
            self.update_enemies(now)
            # redraw
            self.draw_tunnel()
            # self.draw_gui_base()
            self.draw_gui_map()
            self.draw_gui_text()
            dupdate()
        
        # Check for player at wall position (PLAYER_Y - LEVELS == -1)
        if self.GOAL and self.PLAYER_Y == self.GOAL[0] and self.PLAYER_X == self.GOAL[1]:
            if self.try_go_forward_dialog():
                self.regenerate_dungeon()
                return
            else:
                self.PLAYER_Y -= 1
                self.draw_tunnel()
        return None
    
    def update_enemies(self, now):
        for enemy in self.enemies:
            if now - enemy.last_move >= self.enemy_move_interval:
                # Try random direction
                dirs = [(0, 1), (0, -1), (1, 0), (-1, 0)]
                for i in range(len(dirs) - 1, 0, -1):
                    j = random.randint(0, i)
                    dirs[i], dirs[j] = dirs[j], dirs[i]
                    
                for dx, dy in dirs:
                    nx, ny = enemy.x + dx, enemy.y + dy
                    idx = ny * self.MAZE_W + nx
                    if 0 <= nx < self.MAZE_W and 0 <= ny < self.MAZE_H and lsb(self.maze, idx) == 0:
                        enemy.x, enemy.y = nx, ny
                        enemy.last_move = now
                        break

    def draw_gui_base(self):
        # UI panel
        dw, dh = DWIDTH, DHEIGHT
        SCENE_TOP, SCENE_BOTTOM = 0, dh//2
        UI_TOP, UI_BOTTOM = SCENE_BOTTOM, dh
        VANISH_X, VANISH_Y = dw//2, (SCENE_TOP+SCENE_BOTTOM)//2
        LEVELS = 5

        drect(0,UI_TOP,dw,UI_BOTTOM,C_RGB(10,18,17))
        # drect(0,UI_TOP,dw,UI_BOTTOM,C_RGB(2,10,10))
        # dimage(0, UI_TOP, gui_bg)
        # Draw gui_bg image scaled 2x using raw RGB565 data
        src = gui_bg
        palette = []
        for i in range(0, len(src.palette), 2):
            high = src.palette[i]
            low = src.palette[i + 1]
            rgb565 = (high << 8) | low
            r = (rgb565 >> 11) * 255 // 31
            g = ((rgb565 >> 5) & 0x3F) * 255 // 63
            b = (rgb565 & 0x1F) * 255 // 31
            palette.append(C_RGB(r >> 3, g >> 3, b >> 3))

        for y in range(src.height):
            row = y * src.stride
            for x in range(src.width):
                byte = src.data[row + (x >> 1)]
                nibble = (byte >> 4) if (x & 1) == 0 else (byte & 0xF)
                idx = nibble
                color = palette[idx]
                dx, dy = x * 2, UI_TOP + y * 2
                dpixel(dx, dy, color)
                dpixel(dx + 1, dy, color)
                dpixel(dx, dy + 1, color)
                dpixel(dx + 1, dy + 1, color)
    
    def draw_gui_map(self, clean=False):
        # UI panel
        dw, dh = DWIDTH, DHEIGHT
        SCENE_TOP, SCENE_BOTTOM = 0, dh//2
        UI_TOP, UI_BOTTOM = SCENE_BOTTOM, dh

        # Draw background for minimap clip area
        map_x0 = 10
        map_y0 = UI_TOP + 14
        map_x1 = 202
        map_y1 = map_y0 + 128

        if clean:
            drect(map_x0, map_y0, map_x1, map_y1, C_RGB(1, 5, 6))

        # Draw minimap clipped manually to within drect area
        cell = min((map_x1 - map_x0 - 4) // self.MAZE_W, (map_y1 - map_y0 - 4) // self.MAZE_H)
        mx0, my0 = map_x0 + 2, map_y0 + 2

        for ry in range(self.MAZE_H):
            for rx in range(self.MAZE_W):
                idx = ry * self.MAZE_W + rx
                if msb(self.maze, idx) == 0:
                    continue
                x0 = mx0 + rx * cell
                y0 = my0 + ry * cell
                col = C_RGB(2, 9, 10) if lsb(self.maze, idx) == 0 else  C_RGB(0, 3, 3) # C_RGB(1, 5, 6)
                drect(x0, y0, x0 + cell, y0 + cell, col)
                if lsb(self.maze, idx) == 0:
                    if (ry, rx) == self.KEY_POS:
                        drect(x0 + 2, y0 + 2, x0 + cell - 2, y0 + cell - 2, C_RGB(21, 21, 0))
                    if (ry, rx) in self.ITEM_POS:
                        drect(x0 + cell // 4, y0 + cell // 4, x0 + 3 * cell // 4, y0 + 3 * cell // 4, C_RGB(0, 21, 21))

        for e in self.enemies:
            idx = e.y * self.MAZE_W + e.x
            if msb(self.maze, idx):
                ex = mx0 + e.x * cell + 1
                ey = my0 + e.y * cell + 1
                drect(ex, ey, ex + cell - 2, ey + cell - 2, C_RGB(31, 0, 0))  # red box

        # Draw player direction arrow
        px = mx0 + self.PLAYER_X * cell + cell // 2
        py = my0 + self.PLAYER_Y * cell + cell // 2
        dirs = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        dx, dy = dirs[self.cam_dir]
        pdx, pdy = -dy, dx
        dpoly([
            px + dx * cell // 2, py + dy * cell // 2,
            px - pdx * cell // 4, py - pdy * cell // 4,
            px + pdx * cell // 4, py + pdy * cell // 4
        ], C_RGB(6, 15, 15), 1)
    
    def draw_gui_text(self, clean=False):
        # UI panel
        dw, dh = DWIDTH, DHEIGHT
        SCENE_TOP, SCENE_BOTTOM = 0, dh//2
        UI_TOP, UI_BOTTOM = SCENE_BOTTOM, dh

        # Draw background for minimap clip area
        map_x0 = 17
        map_y0 = UI_TOP + 158
        map_y1 = map_y0 + 20

        text_color = C_RGB(6,15,15)

        #TODO: draw icon
        drect(map_x0, map_y0, map_x0+64, map_y0+12, C_RGB(1, 5, 6))
        dtext(map_x0,map_y0,text_color,f"I: {self.item_counter:02}/{self.max_items}")
        #TODO: draw icon
        drect(map_x0, map_y1, map_x0+64, map_y1+12, C_RGB(1, 5, 6))
        dtext(map_x0,map_y1,text_color,f"T: {self.total_score}")
        

    def draw_tunnel(self):
        # clear scene
        # dclear(C_BLACK)
        dw, dh = DWIDTH, DHEIGHT
        SCENE_TOP, SCENE_BOTTOM = 0, dh//2
        UI_TOP, UI_BOTTOM = SCENE_BOTTOM, dh
        VANISH_X, VANISH_Y = dw//2, (SCENE_TOP+SCENE_BOTTOM)//2
        LEVELS = 5

        # direction deltas
        fdy,fdx = self.dir_vectors[self.cam_dir][0]
        ldy,ldx = self.dir_vectors[self.cam_dir][1]
        rdy,rdx = self.dir_vectors[self.cam_dir][2]

        item_markers=[]
        
        # precompute depths
        tvals = [1.0 - 0.5**i for i in range(LEVELS+1)]
        max_shade=30
        step=max_shade//LEVELS
        
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

            shade = max_shade - i*step
            floor_col = self.COLORS_MAP[i][1] # C_RGB(shade,shade,shade)
            ceil_col  = self.COLORS_MAP[i][2] # C_RGB(shade,shade,shade)
            self.left_open = False
            self.right_open = False

            # determine column and row
            # row = PLAYER_Y - i (i=0 nearest slice)
            row = self.PLAYER_Y - i

            # check if wall ahead
            self.forward_block = True
            if 0 <= row - 1 < self.MAZE_H and lsb(self.maze, (row - 1)*self.MAZE_W + self.PLAYER_X) == 1:
                self.forward_block = False

            if 0 <= row < self.MAZE_H:
                if self.PLAYER_X-1>=0 and lsb(self.maze, (row)*self.MAZE_W + self.PLAYER_X-1)==0:
                    self.left_open = True
                if self.PLAYER_X+1<self.MAZE_W and lsb(self.maze, (row)*self.MAZE_W + self.PLAYER_X+1)==0:
                    self.right_open = True
            
            # draw faces
            dpoly(flatten(bl0, br0, br1, bl1), floor_col, 0)
            dpoly(flatten(tl0,tr0,tr1,tl1), ceil_col,   0)

            # -------------------------
            # if there's a corridor on the left, draw the next-inner wall
            if self.left_open and i+1 < LEVELS:
                # compute deeper t2 and corners for sub-wall boundary
                t2 = tvals[i+2]
                bl2 = lerp_point(0, SCENE_BOTTOM, VANISH_X, VANISH_Y, t2)
                tl2 = lerp_point(0, SCENE_TOP,    VANISH_X, VANISH_Y, t2)
                
                left_behind_wall = False
                check_row = row - 1
                check_col = self.PLAYER_X - 1
                if 0 <= check_row < self.MAZE_H and 0 <= check_col < self.MAZE_W:
                    left_behind_wall = (lsb(self.maze, check_row * self.MAZE_W + check_col) == 0)
                
                wall_color = self.COLORS_MAP[i][0]

                # draw roof triangle (red): tl0, tl1, projected (tl0.x, tl1.y)
                x0,y0 = tl0
                x1,y1 = tl1
                dpoly([x0, y0, x1, y1, x0, y1], self.COLORS_MAP[i][2], 0)

                if left_behind_wall:
                    y2 = tl2[1]  # deeper level top Y
                    dpoly([x0, y1, x1, y1, x1, y2], self.COLORS_MAP[i+1][2], 0)


                # draw floor triangle (red): bl0, bl1, projected (bl0.x, bl1.y)
                x0,y0 = bl0
                x1,y1 = bl1
                dpoly([x0, y0, x1, y1, x0, y1], self.COLORS_MAP[i][1], 0)

                if left_behind_wall:
                    y2 = bl2[1]  # deeper level top Y
                    dpoly([x0, y1, x1, y1, x1, bl2[1]], self.COLORS_MAP[i+1][1], 0)

                    # background wall
                    dpoly([bl0[0], bl1[1], bl1[0], bl2[1], tl1[0], tl2[1], tl0[0], tl1[1]], self.COLORS_MAP[i+1][0], 0)
                else:
                    # draw inner wall quad (orange): bl1, bl2, tl2, tl1
                    dpoly([bl1[0], bl1[1], bl0[0], bl1[1], tl0[0], tl1[1], tl1[0], tl1[1]], wall_color, 1)
                    # dpoly([bl1[0], bl1[1], bl2[0], bl2[1], tl2[0], tl2[1], tl1[0], tl1[1]], C_RGB(shade,shade,shade), 1)

                
            elif self.left_open:
                # if too deep, just draw flat left face
                dpoly(flatten(bl0,tl0,tl1,bl1), self.COLORS_MAP[i][0], 0)
            else:
                dpoly(flatten(bl0,tl0,tl1,bl1), self.COLORS_MAP[i][0],  0)

            # if there's a corridor on the right, draw the next-inner wall
            if self.right_open and i+1 < LEVELS:
                # compute t2 for deeper boundary
                t2 = tvals[i+2]
                br2 = lerp_point(dw, SCENE_BOTTOM, VANISH_X, VANISH_Y, t2)
                tr2 = lerp_point(dw, SCENE_TOP,    VANISH_X, VANISH_Y, t2)

                # check if block behind right is a wall (for coloring)
                behind_wall = False
                check_row = row - 1
                check_col = self.PLAYER_X + 1
                if 0 <= check_row < self.MAZE_H and 0 <= check_col < self.MAZE_W:
                    behind_wall = (lsb(self.maze, check_row*self.MAZE_W + check_col) == 0)
                
                wall_color = self.COLORS_MAP[i][0]
                
                # draw roof triangle (red) on right face: tr0, tr1, projected(tr1.x, tr0.y)
                x0, y0 = tr0
                x1, y1 = tr1
                dpoly([x0, y0, x1, y1, x0, y1], self.COLORS_MAP[i][2], 0)

                if behind_wall:
                    y2 = tl2[1]  # deeper level top Y
                    dpoly([x0, y1, x1, y1, x1, y2], self.COLORS_MAP[i+1][2], 0)

                # draw floor triangle (red): br0, br1, project  ed(br1.x, br0.y)
                x0, y0 = br0
                x1, y1 = br1
                dpoly([x0, y0, x1, y1, x0, y1], self.COLORS_MAP[i][1], 0)

                # draw inner wall quad (orange or black)
                if behind_wall:
                    y2 = bl2[1]  # deeper level top Y
                    dpoly([x0, y1, x1, y1, x1, bl2[1]], self.COLORS_MAP[i+1][1], 0)

                    # background wall
                    dpoly([br0[0], br1[1], br1[0], br2[1], tr1[0], tr2[1], tr0[0], tr1[1]], self.COLORS_MAP[i+1][0], 0)
                else:
                    dpoly([br1[0], br1[1], br0[0], br1[1], tr0[0], tr1[1], tr1[0], tr1[1]], self.COLORS_MAP[i][0], 0)
                    # dpoly([br1[0], br1[1], br2[0], br2[1], tr2[0], tr2[1], tr1[0], tr1[1]], C_RGB(shade,shade,shade), 1)
            elif self.right_open:
                dpoly(flatten(br0,tr0,tr1,br1), self.COLORS_MAP[i][0], 0)
            else:
                dpoly(flatten(br0,tr0,tr1,br1), self.COLORS_MAP[i][0], 0)

            # -------------------------
            
            if not self.forward_block or i == LEVELS -1:
                # draw front-facing wall slice at the next depth and stop
                front_col = self.COLORS_MAP[i][0] # C_RGB(shade, shade, shade)
                # use the "far" corners (t1) for the wall position
                dpoly(flatten(tl1, tr1, br1, bl1), front_col, 0)
                break
            
            # draw items behind in perspective (one level)
            depth = i + 1  # next tile depth
            ty = self.PLAYER_Y - depth
            tx = self.PLAYER_X
            if depth <= LEVELS and (ty, tx) in self.ITEM_POS:
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

        obj_flag = self.get_position_flags()

        if obj_flag > 0:
            # TODO: draw another if enemies

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

            if obj_flag & 1:
                color = C_RGB(0,21,21)
            if obj_flag & 2:
                color = C_RGB(21,11,0)
            
            if obj_flag & 4:
                color = C_RGB(21,1,1)
         
            
            drect(mx - half_w, my - half_h, mx + half_w, my + half_h, color)
            # ix0, iy0, ix1, iy1, C_RGB(0,21,21))  # cyan item marker
        
        for (mx, my, half, depth) in item_markers:
            drect(mx - half, my - half, mx + half, my + half, C_RGB(0,21-depth*2,21-depth*2))

    def try_go_forward_dialog(self):
        dw, dh = DWIDTH, DHEIGHT
        SCENE_TOP, SCENE_BOTTOM = 0, dh//2
        UI_TOP, UI_BOTTOM = SCENE_BOTTOM, dh
        VANISH_X, VANISH_Y = dw//2, (SCENE_TOP+SCENE_BOTTOM)//2
        LEVELS = 5

        # upper half overlay
        drect(20, 30, DWIDTH - 20, SCENE_BOTTOM - 20, C_RGB(1, 5, 6))
        dtext(40, 40, C_WHITE, "You've reached a door !")
        dtext(40, 60, C_WHITE, "Press [EXE] to go forward")
        dupdate()

        while True:
            ev = pollevent()
            if ev.type == KEYEV_DOWN:
                if ev.key in [KEY_EXIT, KEY_DOWN, KEY_LEFT, KEY_RIGHT]:
                    return False
                elif ev.key in [KEY_EXE, KEY_UP]:
                    return True
            time.sleep(0.05)
    
    def regenerate_dungeon(self):
        self.total_score += self.item_counter
        seed = random.randint(0, 65535)
        self.generate_dungeon(seed)
        self.redraw_scene_only()

    def get_position_flags(self):
        obj_flag = 0
        if (self.PLAYER_Y, self.PLAYER_X) in self.ITEM_POS:
            obj_flag |= 1
        if (self.PLAYER_Y, self.PLAYER_X ) == self.KEY_POS:
            obj_flag |= 2
        for e in self.enemies:
            if self.PLAYER_X == e.x and self.PLAYER_Y == e.y:
                obj_flag |= 4
                break
        return obj_flag
# --- Menu Scene ---
class MenuScene(Scene):
    items = ["Party", "Items", "Save", "Load", "Exit"]
    X, Y    = 30, 30
    LINE_H  = 20

    def __init__(self):
        super().__init__()
        self.sel=0
    
    def create(self):
        # white background
        drect(20, 20, SCREEN_W-20, SCREEN_H-20, C_WHITE)
        # draw every item once, selection in blue
        for i, txt in enumerate(self.items):
            col = C_BLUE if i == self.sel else C_BLACK
            dtext(self.X, self.Y + i * self.LINE_H, col, txt)
    
    def update(self,t,dt):
        clearevents()
        # if keydown(KEY_EQUALS): return "POP"
        # move selection up
        if keydown(KEY_UP):
            old = self.sel
            new = (old - 1) % len(self.items)
            # erase old line
            drect(20, self.Y + old*self.LINE_H,
                  SCREEN_W-20, self.Y + old*self.LINE_H + self.LINE_H - 1,
                  C_WHITE)
            # redraw old in black, new in blue
            dtext(self.X, self.Y + old*self.LINE_H, C_BLACK, self.items[old])
            self.sel = new
            dtext(self.X, self.Y + new*self.LINE_H, C_BLUE, self.items[new])

        # move selection down
        elif keydown(KEY_DOWN):
            old = self.sel
            new = (old + 1) % len(self.items)
            drect(20, self.Y + old*self.LINE_H,
                  SCREEN_W-20, self.Y + old*self.LINE_H + self.LINE_H - 1,
                  C_WHITE)
            dtext(self.X, self.Y + old*self.LINE_H, C_BLACK, self.items[old])
            self.sel = new
            dtext(self.X, self.Y + new*self.LINE_H, C_BLUE, self.items[new])

        # exit menu
        if keydown(KEY_EXE) or keydown(KEY_EXIT):
            # print(f"Menu selection: {self.items[self.sel]}")
            # TODO: submenu ??
            return "POP"
        
        elif keydown(KEY_EXIT):
            return "POP"
        return None

# --- Game Loop ---
class Game:
    def __init__(self, root_scene:Scene, target_fps=30):
        self.scenes = [root_scene]
        self.target_frame_time = 1.0 / target_fps

        # FPS tracking
        self.fps_last_time = time.monotonic()
        self.fps_accum     = 0
        self.fps           = 0

    def start(self):
        root = self.scenes[0]
        root.running = True
        root.preload(); root.create()
        dupdate() # initial present

        last = time.monotonic()
        while self.scenes:
            now = time.monotonic()
            dt  = now - last
            last = now

            top = self.scenes[-1]
            result = top.update(now, dt)

             # handle push/pop
            if isinstance(result, Scene):
                result.running = True
                result.preload()
                result.create()
                self.scenes.append(result)
                continue
            elif result == "POP":
                top.running = False
                self.scenes.pop()
                if len(self.scenes) > 0:
                    # redraw underlying scene fully
                    base = self.scenes[-1]
                    # dclear(CLEAR_COLOR)
                    base.create()
                    base.update(now, dt)
                    continue


            # FPS box
            self.fps_accum += 1
            if now - self.fps_last_time >= 0.5:
                self.fps = self.fps_accum*2
                self.fps_accum = 0
                self.fps_last_time = now
            
            # BOX_W,BOX_H = 24,12
            # bx = SCREEN_W-BOX_W-2; by=2
            # drect(bx,by,bx+BOX_W-1,by+BOX_H-1,C_WHITE)
            # dtext(bx+2,by,C_BLACK,f"{self.fps:>2}")
            # dupdate()
            
            # cap FPS
            elapsed = time.monotonic() - now
            delay   = self.target_frame_time - elapsed
            if delay>0: time.sleep(delay)

# --- Run ---
game=Game(StartScene(),target_fps=20)
game.start()
