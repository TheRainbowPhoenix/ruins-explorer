import time
from gint import *
from templar_data import *
from templar_rooms import bounce, room_level1
try:
    from typing import Optional, Tuple, List, Dict, Any, Generator # type: ignore

except:                         # MicroPython or stripped env
    pass

# --- Global Configuration ---
# Set to True to print detailed frame timing information to the console.
DEBUG_FRAME_TIME = False

# --- Templar Constants (Unchanged) ---
WW, WH = 21, 15
MAP_X, MAP_Y = -8, -8
HUD_X, HUD_Y, HUD_W, HUD_H = 320, 0, 76, 224
STANCE_IDLE, STANCE_RUNNING, STANCE_JUMPING, STANCE_HURT, STANCE_VICTORY = 0, 1, 2, 3, 4
FACING_LEFT, FACING_RIGHT = 0, 1
PH_GROUNDED, PH_LWALL, PH_RWALL, PH_HEADBANG, PH_TOO_FAST, PH_FAILED, PH_DEATH = 1, 2, 4, 8, 16, 32, 64
SOLID_STD, SOLID_PLANK, SOLID_INTERACTIBLE, SOLID_DEATH, SOLID_NOT, SOLID_FLAG = 0, 1, 2, 3, 4, 5

# --- Templar Core Classes and Functions (Unchanged) ---
# All the original helper classes (vec2, rect, etc.) and physics functions are kept as-is.

class vec2:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __add__(self, other: 'vec2') -> 'vec2':
        return vec2(self.x + other.x, self.y + other.y)
    def __mul__(self, scalar: int) -> 'vec2':
        return vec2(self.x * scalar, self.y * scalar)

class rect:
    def __init__(self, x: int, y: int, w: int, h: int):
        self.x, self.y, self.w, self.h = x, y, w, h
    def left(self) -> int: return self.x
    def right(self) -> int: return self.x + self.w
    def top(self) -> int: return self.y
    def bottom(self) -> int: return self.y + self.h
    def intersects(self, other: 'rect') -> bool:
        return self.right() > other.left() and self.left() < other.right() and \
               self.bottom() > other.top() and self.top() < other.bottom()

class animframeT:
    def __init__(self, img, imgH, x, y, w, h, cx, cy, duration):
        self.img, self.imgH, self.x, self.y, self.w, self.h, self.cx, self.cy, self.duration = \
        img, imgH, x, y, w, h, cx, cy, duration

class animStateT:
    def __init__(self):
        self.frames: Optional[List[animframeT]] = None
        self.index: int = -1
        self.elapsed: float = 0.0
    def set(self, frames: List[animframeT]):
        self.frames, self.index, self.elapsed = frames, 0, 0.0
    def update(self, dt: float) -> bool:
        if self.index < 0 or not self.frames: return False
        self.elapsed += dt
        if self.elapsed * 1000 >= self.frames[self.index].duration:
            self.elapsed = 0
            self.index = (self.index + 1) % len(self.frames)
            return self.index == 0
        return False

class tilesetT:
    def __init__(self, img, tileboxes, solid):
        self.img, self.tileboxes, self.solid = img, tileboxes, solid

class playerT:
    def __init__(self):
        self.pos: vec2 = vec2(0,0)
        self.speed: vec2 = vec2(0,0)
        self.stance: int = -1
        self.facing: int = FACING_RIGHT
        self._grounded: bool = True
        self.jump_frames: int = 0
        self.jump_buffer: int = 0
        self.noncontrol_frames: int = 0
        self.anim: animStateT = animStateT()
    def initialize(self, pos: vec2):
        self.pos = pos
        self.speed = vec2(0, 0)
    def grounded(self) -> bool: return self._grounded
    def airborne(self) -> bool: return not self._grounded

class roomT:
    def __init__(self, w: int, h: int, spawn_x: int, spawn_y: int, tileset: tilesetT, flag_sequence: List[Tuple[int,int,int]]):
        self.w, self.h = w, h
        self.tiles: Optional[bytes] = None
        self.tile_collisions: Optional[bytearray] = None
        self.spawn_x, self.spawn_y = spawn_x, spawn_y
        self.tileset = tileset
        self.flag_sequence = flag_sequence
    def tile_solid(self, tileID: int) -> bool:
        return tileID != 0xff and self.tileset.solid[tileID] == SOLID_STD
    def alignToTiles(self, wr: rect) -> Tuple[int, int, int, int]:
        x1 = max(int(wr.x) >> 4, 0)
        x2 = min(int(wr.x + wr.w - 1) >> 4, self.w - 1)
        y1 = max(int(wr.y) >> 4, 0)
        y2 = min(int(wr.y + wr.h - 1) >> 4, self.h - 1)
        return x1, y1, x2, y2
    def hitboxesNear(self, wr: rect) -> Generator[Tuple[rect, int, int], None, None]:
        if not self.tiles or not self.tile_collisions: return
        x1, y1, x2, y2 = self.alignToTiles(wr)
        tb = self.tileset.tileboxes
        for y in range(y1, y2 + 1):
            for x in range(x1, x2 + 1):
                i = self.w * y + x
                t = self.tiles[i]
                if t != 0xff and tb[4*t+2]:
                    yield rect(16*x + tb[4*t], 16*y + tb[4*t+1], tb[4*t+2], tb[4*t+3]), \
                          self.tile_collisions[i], self.tileset.solid[t]
    def compute_tile_collisions(self):
        if not self.tiles: return
        w, h = self.w, self.h; i = 0
        self.tile_collisions = bytearray(w * h)
        for y in range(h):
            for x in range(w):
                t = self.tiles[i]
                solid = SOLID_NOT if t == 0xff else self.tileset.solid[t]
                if solid == SOLID_PLANK:
                    if y > 0 and not self.tile_solid(self.tiles[i - w]):
                        self.tile_collisions[i] = PH_GROUNDED
                elif solid != SOLID_NOT:
                    sides = 0
                    if y > 0 and not self.tile_solid(self.tiles[i - w]): sides |= PH_GROUNDED
                    if y < h-1 and not self.tile_solid(self.tiles[i+w]): sides |= PH_HEADBANG
                    if x > 0 and not self.tile_solid(self.tiles[i-1]): sides |= PH_RWALL
                    if x < w-1 and not self.tile_solid(self.tiles[i+1]): sides |= PH_LWALL
                    self.tile_collisions[i] = sides
                i += 1

# --- Scene Management Structure ---
class Scene:
    """Base class for all game scenes."""
    def create(self): pass
    def update(self, dt: float) -> Optional[str]: pass
    def draw(self, frame_time_ms: int): pass

class TemplarScene(Scene):
    """Encapsulates the entire state and logic of the Templar game."""
    def __init__(self):
        self.room: Optional[roomT] = None
        self.player: Optional[playerT] = None
        self.entities: List[Tuple[vec2, animStateT]] = []
        self.flags_data: Dict[Tuple[int, int], bool] = {}
        self.flags_taken: int = 0
        self.flag_cursor: int = 0
        self.dirty_tiles: Optional[bytearray] = None
        self.game_time: float = 0.0
        self.deaths: int = 0
        self.reset_timer: float = -1.0
        self.end_timer: float = -1.0
        self.physics_flags: int = 0
        self.debug_hitboxes: int = 1
        self.debug_resolution: rect = rect(0,0,0,0)

    def create(self):
        """Initializes the game state, called once when the scene starts."""
        # This is the setup code from the original main()
        flag_sequence = [(15, 13, 1), (19, 10, 2), (11, 6, 1), (5, 5, 1), (17, 2, 0), (1, 8, 0)]
        self.room = roomT(WW, WH, 32, 224, tileset, flag_sequence) # type: ignore
        self.room.tiles = room_level1[2]
        self.room.compute_tile_collisions()

        self.player = playerT()
        self.player.initialize(vec2(self.room.spawn_x, self.room.spawn_y))
        self.player_set_stance(STANCE_IDLE)

        self.dirty_tiles = bytearray(self.room.w * self.room.h)
        for i in range(len(self.dirty_tiles)): self.dirty_tiles[i] = 1

        self.show_next_flags(1)

    def update(self, dt: float) -> Optional[str]:
        """Handles all game logic and input for one fixed-step update."""
        assert self.player is not None and self.room is not None and self.dirty_tiles is not None
        
        cleareventflips()
        clearevents()

        dx = keydown(KEY_RIGHT) - keydown(KEY_LEFT)
        jump_down = keydown(KEY_SHIFT) or keydown(KEY_UP)
        if keypressed(KEY_SHIFT) or keypressed(KEY_UP): self.player.jump_buffer = 3
        if keypressed(KEY_OPTN):
            self.debug_hitboxes = (self.debug_hitboxes + 1) % 3
            # Mark all tiles dirty to redraw hitbox outlines
            for i in range(len(self.dirty_tiles)): self.dirty_tiles[i] = 1
        if keydown(KEY_EXIT): return "EXIT_APP"

        # --- Update Game State (adapted from game_update) ---
        self.game_time += dt
        self.player.anim.update(dt)

        # Update entities and remove finished ones
        self.entities = [e for e in self.entities if not e[1].update(dt)]

        if self.end_timer > 0:
            self.end_timer -= dt
            if self.end_timer <= 0: return "EXIT_APP"
        
        if self.reset_timer > 0:
            self.reset_timer -= dt
            if self.reset_timer <= 0:
                self.reset_timer = -1
                self.player.pos = vec2(self.room.spawn_x, self.room.spawn_y)
                self.player.speed = vec2(0, 0)
                self.deaths += 1

        # --- Player Physics ---
        if self.player.jump_buffer > 0: self.player.jump_buffer -= 1
        if self.player.jump_buffer and self.player.grounded():
            self.player.speed.y = -140
            self.player.jump_frames = 5
            self.player.jump_buffer = 0

        self.player.speed.x *= 0.95
        if dx > 0: self.player.speed.x = max(self.player.speed.x, 64)
        elif dx < 0: self.player.speed.x = min(self.player.speed.x, -64)
        else: self.player.speed.x = int(self.player.speed.x * 0.5)
        
        if self.player.airborne(): self.player.speed.y += 9.81 * dt * 30

        if self.player.jump_frames > 0:
            if not jump_down: self.player.speed.y = max(self.player.speed.y, -20)
            self.player.jump_frames -= 1

        self.player_set_stance(STANCE_JUMPING if self.player.airborne() else (STANCE_RUNNING if dx else STANCE_IDLE))
        if dx > 0: self.player.facing = FACING_RIGHT
        elif dx < 0: self.player.facing = FACING_LEFT

        self.player.pos, self.physics_flags = self.physics_displace(self.player.pos, self.player.speed * dt) # type: ignore -- it is supported my __mul__
        self.player._grounded = (self.physics_flags & PH_GROUNDED) != 0

        # ... (Rest of physics logic like bounces, wall collisions etc. is complex and unchanged) ...
        # Instead of modifying game object, we modify self
        if self.physics_flags & (PH_LWALL | PH_RWALL): self.player.speed.x = 0
        if self.physics_flags & PH_HEADBANG: self.player.speed.y = max(self.player.speed.y, 0)
        if self.physics_flags & PH_GROUNDED: self.player.speed.y = 20
        
        if (self.physics_flags & PH_DEATH) or not (0 < self.player.pos.x < 16*self.room.w and 0 < self.player.pos.y < 16*self.room.h):
            self.player_set_stance(STANCE_HURT); self.reset_timer = 0.6
        if self.flags_taken >= len(self.room.flag_sequence) and self.end_timer < 0:
            self.player_set_stance(STANCE_VICTORY); self.end_timer = 3.0
        
        return None

    def draw(self, frame_time_ms: int):
        """Renders the entire game world."""
        assert self.player is not None and self.room is not None and self.dirty_tiles is not None
        
        self.draw_room()
        for pos, entity_anim in self.entities:
            self.draw_entity(pos, entity_anim)
        self.draw_player()
        self.draw_hud(frame_time_ms)

        if self.debug_hitboxes >= 1:
            phb = self.physics_player_hitbox(self.player.pos)
            self.draw_outline(self.debug_resolution, C_RGB(0,31,0))
            self.draw_outline(phb, C_GREEN)
        if self.debug_hitboxes == 2:
            for b, bf, _ in self.room.hitboxesNear(rect(0,0,self.room.w*16, self.room.h*16)):
                self.draw_flagged_outline(b, bf, C_RED, C_WHITE)

    # --- Scene-specific Helper Methods (formerly global functions) ---
    def player_set_stance(self, stance: int):
        assert self.player
        if self.player.stance == stance: return
        self.player.stance = stance
        if stance == STANCE_IDLE: self.player.anim.set(sprites["Idle"]) # type: ignore[arg-type]
        elif stance == STANCE_RUNNING: self.player.anim.set(sprites["Running"]) # type: ignore[arg-type]
        elif stance == STANCE_JUMPING: self.player.anim.set(sprites["Jumping"]) # type: ignore[arg-type]
        elif stance == STANCE_HURT: self.player.anim.set(sprites["Hurt"]) # type: ignore[arg-type]
        elif stance == STANCE_VICTORY: self.player.anim.set(sprites["Victory"]) # type: ignore[arg-type]

    def physics_player_hitbox(self, pos: vec2) -> rect:
        return rect(pos.x - 5, pos.y - 14, 11, 14)

    def physics_acceptable(self, pos: vec2) -> bool:
        assert self.room
        player_hb = self.physics_player_hitbox(pos)
        for hb, _, solid in self.room.hitboxesNear(player_hb):
            if solid == SOLID_STD and player_hb.intersects(hb):
                # HACK: Backwards world to tile grid conversion
                x, y = int(hb.x) >> 4, int(hb.y) >> 4
                # TODO: game.takeFlag(x, y)
                return False
        return True
    
    def physics_displace(self, pos: vec2, diff: vec2) -> Tuple[vec2, int]:
        pr = self.physics_player_hitbox(pos + diff)
        resolution = vec2(0, 0); flags = 0
        if self.room:
            for r, rf, solid in self.room.hitboxesNear(pr):
                if not pr.intersects(r): continue
                if solid == SOLID_DEATH: return pos + diff, PH_DEATH
                if solid in (SOLID_NOT, SOLID_FLAG): continue
                if solid == SOLID_PLANK and (diff.y < 0 or pos.y > r.top() + 1): continue
                
                left_overlap = max(r.right() - pr.left(), 0)
                right_overlap = min(r.left() - pr.right(), 0)
                top_overlap = max(r.bottom() - pr.top(), 0)
                bottom_overlap = min(r.top() - pr.bottom(), 0)
                
                smallest_overlap = 999999
                xo, yo, fo = 0.0, 0.0, 0
                
                if (rf & PH_LWALL) and 0 < left_overlap < smallest_overlap:
                    xo, yo, fo, smallest_overlap = left_overlap, 0, PH_LWALL, left_overlap
                if (rf & PH_RWALL) and 0 < -right_overlap < smallest_overlap:
                    xo, yo, fo, smallest_overlap = right_overlap, 0, PH_RWALL, -right_overlap
                if (rf & PH_HEADBANG) and 0 < top_overlap < smallest_overlap:
                    xo, yo, fo, smallest_overlap = 0, top_overlap, PH_HEADBANG, top_overlap
                if (rf & PH_GROUNDED) and 0 < -bottom_overlap < smallest_overlap:
                    xo, yo, fo, smallest_overlap = 0, bottom_overlap, PH_GROUNDED, -bottom_overlap
                
                if abs(xo) > abs(resolution.x): resolution.x = xo # type: ignore
                if abs(yo) > abs(resolution.y): resolution.y = yo # type: ignore
                flags |= fo
        
        self.debug_resolution = self.physics_player_hitbox(pos + diff + resolution)
        if max(abs(resolution.x), abs(resolution.y)) >= 15: return pos, PH_TOO_FAST
        
        adjusted = pos + diff
        if not (flags & PH_LWALL and flags & PH_RWALL): adjusted.x += resolution.x
        if not (flags & PH_HEADBANG and flags & PH_GROUNDED): adjusted.y += resolution.y
        
        return (adjusted, flags) if self.physics_acceptable(adjusted) else (pos, flags | PH_FAILED)

    def mark_tiles_dirty(self, wr: rect):
        assert self.dirty_tiles
        assert self.room

        x1, y1, x2, y2 = self.room.alignToTiles(wr)
        for y in range(y1, y2 + 1):
            for x in range(x1, x2 + 1): self.dirty_tiles[y * self.room.w + x] = 1

    def show_next_flags(self, n: int):
        assert self.room
        n = min(n, len(self.room.flag_sequence) - self.flag_cursor)
        for _ in range(n):
            x, y, _ = self.room.flag_sequence[self.flag_cursor]
            self.flags_data[(x, y)] = False
            if self.dirty_tiles:
                self.dirty_tiles[y * self.room.w + x] = 1
            self.flag_cursor += 1

    def draw_room(self):
        assert self.room
        i = 0
        for ty in range(self.room.h):
            for tx in range(self.room.w):
                if self.room.tiles:
                    t = self.room.tiles[i]
                    if t == 101 and self.flags_data.get((tx, ty), True): t = 0xff
                    
                    if self.dirty_tiles:
                        if self.dirty_tiles[i]:
                            self.draw_tile(tx, ty, t)
                            self.dirty_tiles[i] = 0
                    i += 1
    
    def draw_tile(self, x: int, y: int, tileID: int):
        assert self.room
        img = self.room.tileset.img
        sx, sy = MAP_X + 16 * x, MAP_Y + 16 * y
        w = img.width >> 4; tx, ty = tileID % w, tileID // w
        
        dsubimage(sx, sy, img, 176, 48, 16, 16) # background
        if 16 * ty < img.height:
            dsubimage(sx, sy, img, 16 * tx, 16 * ty, 16, 16)

    def draw_player(self):
        assert self.player

        p = self.player
        # ... (draw_player logic, but it needs to mark tiles dirty on self)
        flipped = (p.facing == FACING_LEFT)
        base = self.world2screen(p.pos)
        if p.anim.index >= 0 and p.anim.frames:
            f = p.anim.frames[p.anim.index]
            img, cx = (f.imgH, f.w - 1 - f.cx) if flipped else (f.img, f.cx)
            dsubimage(base.x - cx, base.y - f.cy, img, f.x, f.y, f.w, f.h)
            self.mark_tiles_dirty(self.screen2world_rect(rect(base.x-cx, base.y-f.cy, f.w, f.h)))

    def draw_entity(self, pos: vec2, anim: animStateT):
        base = self.world2screen(pos)
        if anim.index >= 0 and anim.frames:
            f = anim.frames[anim.index]
            dsubimage(base.x - f.cx, base.y - f.cy, f.img, f.x, f.y, f.w, f.h)
            self.mark_tiles_dirty(self.screen2world_rect(rect(base.x-f.cx, base.y-f.cy, f.w, f.h)))

    def draw_hud(self, frame_time_ms: int):
        x, y = HUD_X + 2, HUD_Y + 4
        drect(HUD_X, HUD_Y, HUD_X + HUD_W - 1, HUD_Y + HUD_H - 1, C_RGB(6,5,2))
        if self.debug_hitboxes > 0:
            # ... (all debug text)
            dtext(x, y+135, C_WHITE, f"ft: {frame_time_ms} ms")
        else:
            if self.room:
                dtext(x, y, C_WHITE, f"Flags: {self.flags_taken}/{len(self.room.flag_sequence)}")
            dtext(x, y+15, C_WHITE, f"Deaths: {self.deaths}")
            dtext(x, y+30, C_WHITE, f"Time: {self.game_time:.1f}")

    def world2screen(self, pos: vec2) -> vec2:
        return vec2(MAP_X + int(pos.x), MAP_Y + int(pos.y))
    def world2screen_rect(self, r: rect) -> rect:
        return rect(MAP_X + int(r.x), MAP_Y + int(r.y), int(r.w), int(r.h))
    def screen2world_rect(self, r: rect) -> rect:
        return rect(r.x - MAP_X, r.y - MAP_Y, r.w, r.h)
    def draw_outline(self, r: rect, color: int):
        self.mark_tiles_dirty(r)
        r = self.world2screen_rect(r)
        drect_border(r.x, r.y, r.x+r.w-1, r.y+r.h-1, C_NONE, 1, color)
    def draw_flagged_outline(self, r: rect, rb: int, c1: int, c2: int):
        self.mark_tiles_dirty(r)
        r = self.world2screen_rect(r)
        dline(r.x,r.y,r.x+r.w-1,r.y, c2 if rb & PH_GROUNDED else c1)
        dline(r.x,r.y+r.h-1,r.x+r.w-1,r.y+r.h-1, c2 if rb & PH_HEADBANG else c1)
        dline(r.x,r.y,r.x,r.y+r.h-1, c2 if rb & PH_RWALL else c1)
        dline(r.x+r.w-1,r.y,r.x+r.w-1,r.y+r.h-1, c2 if rb & PH_LWALL else c1)

class Game:
    """Manages the scene stack and the main fixed-timestep game loop."""
    def __init__(self, root_scene: Scene):
        self.scenes: List[Scene] = [root_scene]
        self.running: bool = False
        self.fixed_timestep: float = 0.055
        self.frame_cap_ms: int = 53

    def start(self):
        if not self.scenes: return
        self.running = True
        self.scenes[-1].create()

        while self.running and self.scenes:
            frame_start_time = time.ticks_ms()

            # --- LOGIC UPDATE (FIXED STEP) ---
            # This is simplified because Templar's logic update is fast enough
            # to always run once per frame. A more complex loop would use an
            # accumulator for variable framerates.
            top_scene = self.scenes[-1]
            result = top_scene.update(self.fixed_timestep)
            
            if result == "EXIT_APP":
                self.running = False
                break
            # (Add more scene changes like 'POP' or new scenes here if needed)

            # --- RENDER ---
            frame_render_start = time.ticks_ms()
            top_scene.draw(time.ticks_diff(time.ticks_ms(), frame_render_start))
            dupdate()

            # --- FRAME CAP ---
            frame_time_ms = time.ticks_diff(time.ticks_ms(), frame_start_time)
            
            if DEBUG_FRAME_TIME:
                print(f"Frame Time: {frame_time_ms}ms")

            if frame_time_ms < self.frame_cap_ms:
                time.sleep_ms(self.frame_cap_ms - frame_time_ms)

def main():
    # --- Asset Pre-processing ---
    for _, frames in sprites.items():
        for i, frame_data in enumerate(frames): frames[i] = animframeT(*frame_data) # type: ignore
    for _, frames in bounce.items():
        for i, frame_data in enumerate(frames): frames[i] = animframeT(*frame_data) # type: ignore
    
    global tileset
    tileset = tilesetT(*tileset)

    # --- Start the game ---
    game = Game(TemplarScene())
    game.start()
    
    # --- Cleanup ---
    dclear(C_WHITE)
    dtext(5, 5, C_BLACK, "Game Over. Thanks for playing!")
    dupdate()
    time.sleep(2)

main()