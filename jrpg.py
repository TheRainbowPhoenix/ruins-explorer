import random
import time
from gint import *

# --- constants ---
TILE_SIZE    = 20
TILE_COLS    = 16
TILE_ROWS    = 10
SCREEN_W     = DWIDTH
SCREEN_H     = DHEIGHT
MAP_COLS     = 50
MAP_ROWS     = 50

SCREEN_TILES_X  = DWIDTH // TILE_SIZE
SCREEN_TILES_Y  = DHEIGHT // TILE_SIZE

CLEAR_COLOR     = C_RGB(31,31,31)

KEY_MENU = KEY_EQUALS

# load your 320×200 tileset
# smario_tiles.image is assumed to be an Image object
from fanta_tiles import image as tileset_img

TID_SIGN  = 4
OBJECT_TILES = [52, 53]
# the set of impassable tile IDs
BLOCKED   = { TID_SIGN }

# Helpers to snap tile‐coords to the current “screen” block
def screen_block(px, tiles_w):
    return px // tiles_w

# --- Camera ---
class Camera:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

# --- Scene Base ---
class Scene:
    def __init__(self):
        self.camera = Camera()
        self.running = False

    def preload(self): pass
    def create(self): pass
    def update(self, t, dt): pass

# --- JRPG Scene ---
class JRPGScene(Scene):
    def __init__(self):
        super().__init__()

        # Random map: 0…(TILE_COLS*TILE_ROWS-1)
        self.cols = 50
        self.rows = 50

        # 1) Base: plains/grass
        base_choices = [1, 2]       # tile indices 1=plain, 2=grass
        self.map = [
            [ random.choice(base_choices) for _ in range(self.cols) ]
            for __ in range(self.rows)
        ]

        # 2) Dirt+flower patches
        num_patches = 30
        for _ in range(num_patches):
            # pick a random patch center
            cx = random.randrange(self.cols)
            cy = random.randrange(self.rows)
            # random “radius” of the blob
            radius = random.randrange(3, 7)
            for dy in range(-radius, radius+1):
                for dx in range(-radius, radius+1):
                    # Manhattan distance to keep it blob‑shaped
                    if abs(dx) + abs(dy) > radius:
                        continue
                    x = cx + dx
                    y = cy + dy
                    if 0 <= x < self.cols and 0 <= y < self.rows:
                        # 70% dirt(5), 30% flowers(6)
                        self.map[y][x] = 5 if random.random() < 0.7 else 6
        
        # 3) Signs
        self.signs = {}
        for i in range(8):
            sx = random.randrange(self.cols)
            sy = random.randrange(self.rows)
            self.map[sy][sx] = TID_SIGN
            # each sign has 2–4 pages of dummy text
            pages = [
                f"Sign #{i+1}, page {p+1}\nHello from sign {i+1}!"
                for p in range(random.randrange(2,5))
            ]
            self.signs[(sx,sy)] = pages
        
        # 4) Objects layer
        self.objects = {}
        for i in range(12):
            ox = random.randrange(self.cols)
            oy = random.randrange(self.rows)
            # don’t place on a sign or on the player spawn
            if (ox,oy) in self.signs or (ox,oy) == (self.cols//2,self.rows//2):
                continue
            tile_idx = random.choice(OBJECT_TILES)
            pages = [ f"Object #{i+1}, page {p+1}\nYou found object {i+1}!"
                  for p in range(random.randrange(1,4)) ]
            self.objects[(ox,oy)] = (tile_idx, pages)

        # 5) Player
        self.px = self.cols // 2
        self.py = self.rows // 2

        # 6) Precompute src coords once
        self.src = []
        for idx in range(TILE_COLS * TILE_ROWS):
            sx = (idx % TILE_COLS) * TILE_SIZE
            sy = (idx // TILE_COLS) * TILE_SIZE
            self.src.append((sx, sy))
        
        # dialog state
        self.dialog_active = False
        self.dialog_pages  = []
        self.dialog_index  = 0
        self.arrow_offset = 0
        self.arrow_dir    = 1

    def create(self):
        self._update_camera_block()
        # draw full viewport once
        dclear(CLEAR_COLOR)
        self._draw_viewport()
        self._draw_player()

    def update(self, t, dt):
        # if in dialog mode, only handle EXE to advance/exit
        if self.dialog_active:
            clearevents()

            if keydown(KEY_EXE):
                self.dialog_index += 1
                if self.dialog_index >= len(self.dialog_pages):
                    # end dialog → redraw map & player, then exit dialog
                    self.dialog_active = False
                    self._draw_viewport()
                    self._draw_player()
                    return
                else:
                    # next page: redraw dialog
                    pass
            # always redraw dialog box
            self._draw_dialog_box()
            # --- arrow animation ---

            # bounce offset by ±1 each frame, clamp at ±2
            self.arrow_offset += self.arrow_dir
            if abs(self.arrow_offset) >= 2:
                self.arrow_dir *= -1

            # compute box position
            box_h = DHEIGHT // 4
            y0    = DHEIGHT - box_h

            A_W,A_H = 6,6
            ax = SCREEN_W - 8 - A_W
            ay = y0 + 8 + self.arrow_offset

            # clear just that little area to dialog background (white)
            drect(ax,            ay,
                  ax + A_W - 1, ay + A_H - 1,
                  C_WHITE)
            dpoly([ax,ay, ax+A_W-1,ay, ax+A_W//2,ay+A_H-1],
                  C_NONE, C_BLACK)

            return
        
        # normal mode: movement + EXE to trigger
        old_px, old_py = self.px, self.py
        old_block = (self.cam_block_x, self.cam_block_y)

        # 1) handle input
        clearevents()
        if keydown(KEY_EXIT):
            self.running = False
            return
        
        if keydown(KEY_MENU):
            return MenuScene()     # push menu
        
        # attempt 4‑way move if walkable
        for KEY, dx, dy in (
            (KEY_LEFT, -1,  0),
            (KEY_RIGHT, 1,  0),
            (KEY_UP,    0, -1),
            (KEY_DOWN,  0,  1),
        ):
            if keydown(KEY):
                nx, ny = self.px+dx, self.py+dy
                if 0<=nx<self.cols and 0<=ny<self.rows and self.map[ny][nx] not in BLOCKED:
                    self.px, self.py = nx, ny
                break
        
        # press EXE to interact
        if keydown(KEY_EXE):
            # 1) if standing on an object, trigger it
            pos = (self.px, self.py)
            if pos in self.objects:
                tile_idx, pages = self.objects[pos]
                self.dialog_active = True
                self.dialog_pages  = pages
                self.dialog_index  = 0
                self._draw_dialog_box()
                return

            # 2) else if adjacent to a sign, trigger sign
            for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
                pos2 = (self.px+dx, self.py+dy)
                if pos2 in self.signs:
                    pages = self.signs[pos2]
                    self.dialog_active = True
                    self.dialog_pages  = pages
                    self.dialog_index  = 0
                    self._draw_dialog_box()
                    return
        

        # update camera block if needed
        self._update_camera_block()
        new_block = (self.cam_block_x, self.cam_block_y)

        if new_block != old_block:
            # full redraw on block switch
            dclear(CLEAR_COLOR)
            self._draw_viewport()
            self._draw_player()
        else:
            # only redraw old tile + player
            self._draw_tile_at(old_px, old_py)
            self._draw_player()

    # --- helpers ---
    def _update_camera_block(self):
        bx = screen_block(self.px, SCREEN_TILES_X)
        by = screen_block(self.py, SCREEN_TILES_Y)
        self.cam_block_x = bx
        self.cam_block_y = by
        # pixel‐aligned camera in tiles
        self.camera.x = bx * SCREEN_TILES_X * TILE_SIZE
        self.camera.y = by * SCREEN_TILES_Y * TILE_SIZE

    def _draw_viewport(self):
        """Draw all tiles in the current camera block."""
        base_x = self.cam_block_x * SCREEN_TILES_X
        base_y = self.cam_block_y * SCREEN_TILES_Y

        # How many tiles remain in the map at this block?
        rows = min(SCREEN_TILES_Y, self.rows-base_y)
        cols = min(SCREEN_TILES_X, self.cols-base_x)

        for ry in range(rows):
            my = base_y + ry
            for cx in range(cols):
                mx = base_x + cx
                idx    = self.map[my][mx]
                sx,sy  = self.src[idx]
                dsubimage(cx*TILE_SIZE, ry*TILE_SIZE,
                          tileset_img, sx, sy,
                          TILE_SIZE, TILE_SIZE)
                # draw object layer if present
                if (mx,my) in self.objects:
                    tile_idx, _ = self.objects[(mx,my)]
                    sx2, sy2 = self.src[tile_idx]
                    dsubimage(
                        cx * TILE_SIZE, ry * TILE_SIZE,
                        tileset_img, sx2, sy2,
                        TILE_SIZE, TILE_SIZE
                    )

    def _draw_tile_at(self, px, py):
        """Redraw exactly one tile of the map at tile‑coords (px,py)."""
        sx = px * TILE_SIZE - self.camera.x
        sy = py * TILE_SIZE - self.camera.y
        idx = self.map[py][px]
        src_x, src_y = self.src[idx]
        dsubimage(sx, sy,
                  tileset_img,
                  src_x, src_y,
                  TILE_SIZE, TILE_SIZE)
        # object on top?
        if (px,py) in self.objects:
            tile_idx, _ = self.objects[(px,py)]
            sx2, sy2 = self.src[tile_idx]
            dsubimage(
                sx, sy,
                tileset_img, sx2, sy2,
                TILE_SIZE, TILE_SIZE
            )

    def _draw_player(self):
        """Draw the player (blue circle) at its current pos."""
        cx = self.px * TILE_SIZE - self.camera.x + TILE_SIZE//2
        cy = self.py * TILE_SIZE - self.camera.y + TILE_SIZE//2
        # radius a bit smaller than tile
        dcircle(cx, cy, TILE_SIZE//2 - 2, C_BLUE, C_NONE)
    

    def _draw_dialog_box(self):
        # box at bottom quarter
        box_h = DHEIGHT // 4
        y0    = DHEIGHT - box_h
        drect(  0,     y0, DWIDTH-1, DHEIGHT-1, C_WHITE)
        drect(  0,     y0, DWIDTH-1, y0,       C_BLACK)  # top border
        # render current page, split lines
        page = self.dialog_pages[self.dialog_index]
        lines = page.split("\n")
        for i, line in enumerate(lines):
            dtext(8, y0 + 8 + i*16, C_BLACK, line)


class BattleScene(Scene):
    def create(self):
        # full‐screen battle UI
        dclear(C_RGB(15,0,0))
        dtext(100,100,C_WHITE,"Battle Start!")
    def update(self, t, dt):
        clearevents()
        if keydown(KEY_EXE):
            return "POP"

class MenuScene(Scene):
    items = ["Party", "Items", "Save", "Load", "Exit"]
    X, Y    = 30, 30
    LINE_H  = 20

    def __init__(self):
        super().__init__()
        self.sel = 0

    def create(self):
        # white background
        drect(20, 20, SCREEN_W-20, SCREEN_H-20, C_WHITE)
        # draw every item once, selection in blue
        for i, txt in enumerate(self.items):
            col = C_BLUE if i == self.sel else C_BLACK
            dtext(self.X, self.Y + i * self.LINE_H, col, txt)

    def update(self, t, dt):
        clearevents()

        if keydown(KEY_MENU):
            return "POP"

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
            print(f"Menu selection: {self.items[self.sel]}")
            # TODO: submenu ??
            return "POP"
        
        elif keydown(KEY_EXIT):
            return "POP"

# --- Game with full‑screen update ---
class Game:
    def __init__(self, root_scene: Scene, target_fps=30):
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
            dt  = now - last; last = now

            top = self.scenes[-1]
            result = top.update(now, dt)

            # handle push/pop
            if isinstance(result, Scene):
                result.running = True
                result.preload(); result.create()
                self.scenes.append(result)
                continue
            elif result == "POP":
                top.running = False
                self.scenes.pop()
                # redraw underlying scene fully
                base = self.scenes[-1]
                dclear(CLEAR_COLOR)
                base.create()
                continue

            # draw FPS
            self.fps_accum += 1
            if now - self.fps_last_time >= 0.5:
                self.fps = self.fps_accum*2
                self.fps_accum = 0
                self.fps_last_time = now

            BOX_W,BOX_H = 24,12
            bx = SCREEN_W-BOX_W-2; by=2
            drect(bx,by,bx+BOX_W-1,by+BOX_H-1,C_WHITE)
            dtext(bx+2,by,C_BLACK,f"{self.fps:>2}")

            dupdate()

            # cap FPS
            elapsed = time.monotonic() - now
            delay   = self.target_frame_time - elapsed
            if delay>0: time.sleep(delay)

# --- run it ---
game = Game(JRPGScene(), target_fps=10)
game.start()
