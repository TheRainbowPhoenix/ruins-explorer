# scenes/templar_scene.py
# The complete Templar platformer game, refactored into a Scene.

from gint import *
try:
    from typing import Optional, Tuple, List, Dict, Any, Generator
except:                         # MicroPython or stripped env
    pass

# Engine imports
from cpgame.engine.scene import Scene
from cpgame.engine.geometry import Vec2, Rect
from cpgame.engine.animation import AnimationState, AnimationVariantManager
from cpgame.engine.assets import Tilemap, AssetManager

# --- Scene-Specific Constants ---
# We use fixed-point math to avoid floats. All positions and speeds are
# scaled up by 2^8, and then scaled down for rendering.
FIXED_POINT_SHIFT = 8

# Viewport and HUD layout
WW, WH = 21, 15
MAP_X, MAP_Y = -8, -8
HUD_X, HUD_Y, HUD_W, HUD_H = 320, 0, 76, 224

# Player and physics states
STANCE_IDLE, STANCE_RUNNING, STANCE_JUMPING, STANCE_HURT, STANCE_VICTORY = 0, 1, 2, 3, 4
FACING_LEFT, FACING_RIGHT = 0, 1
PH_GROUNDED, PH_LWALL, PH_RWALL, PH_HEADBANG, PH_TOO_FAST, PH_FAILED, PH_DEATH = 1, 2, 4, 8, 16, 32, 64
SOLID_STD, SOLID_PLANK, SOLID_INTERACTIBLE, SOLID_DEATH, SOLID_NOT, SOLID_FLAG = 0, 1, 2, 3, 4, 5


# --- Templar-Specific Data Structures ---
# These classes are tightly coupled with this scene's logic.

class PlayerEntity:
    """Holds all state for the player character."""
    def __init__(self):
        self.pos: Vec2 = Vec2(0,0)
        self.speed: Vec2 = Vec2(0,0)
        self.stance: int = -1
        self.facing: int = FACING_RIGHT
        self._grounded: bool = True
        self.jump_frames: int = 0
        self.jump_buffer: int = 0
        self.noncontrol_frames: int = 0
        self.anim: AnimationState = AnimationState()

    def initialize(self, pos: Vec2):
        # Initial position is in pixels, so we scale it up to fixed-point.
        self.pos = Vec2(pos.x, pos.y)
        self.speed = Vec2(0, 0)

    def grounded(self) -> bool: return self._grounded
    def airborne(self) -> bool: return not self._grounded

class RoomEntity:
    """Holds all data for a single level or room."""
    def __init__(self, w: int, h: int, spawn_x: int, spawn_y: int, tileset: Tilemap, flag_sequence: List):
        self.w, self.h = w, h
        self.tiles: Optional[bytes] = None
        self.tile_collisions: Optional[bytearray] = None
        self.spawn_x, self.spawn_y = spawn_x, spawn_y
        self.tileset = tileset
        self.flag_sequence = flag_sequence

    def tile_solid(self, tileID: int) -> bool:
        return tileID != 0xff and self.tileset.solid[tileID] == SOLID_STD

    def alignToTiles(self, wr: Rect) -> Tuple[int, int, int, int]:
        # Convert fixed-point Rect to tile grid coordinates
        x1 = max(int(wr.x) >> 4, 0)
        x2 = min(int(wr.x + wr.w - 1) >> 4, self.w - 1)
        y1 = max(int(wr.y) >> 4, 0)
        y2 = min(int(wr.y + wr.h - 1) >> 4, self.h - 1)
        return x1, y1, x2, y2

    def hitboxesNear(self, wr: Rect) -> Generator[Tuple[Rect, int, int], None, None]:
        if not self.tiles or not self.tile_collisions: return
        x1, y1, x2, y2 = self.alignToTiles(wr)
        tb = self.tileset.tileboxes
        for y in range(y1, y2 + 1):
            for x in range(x1, x2 + 1):
                i = self.w * y + x
                t = self.tiles[i]
                if t != 0xff and tb[4*t+2]:
                    yield Rect(
                        (16*x + tb[4*t]),
                        (16*y + tb[4*t+1]),
                        tb[4*t+2],
                        tb[4*t+3]
                    ), self.tile_collisions[i], self.tileset.solid[t]

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

# --- The Main Templar Scene Class ---

class TemplarScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        # --- Game State Attributes ---
        self.room: Optional[RoomEntity] = None
        self.player: Optional[PlayerEntity] = None
        self.entities: List[Tuple[Vec2, AnimationState]] = []
        self.flags_data: Dict[Tuple[int, int], bool] = {}
        self.flags_taken: int = 0
        self.flag_cursor: int = 0
        self.dirty_tiles: Optional[bytearray] = None
        self.game_time: float = 0.0
        self.deaths: int = 0
        self.reset_timer: float = -1.0
        self.end_timer: float = -1.0
        self.physics_flags: int = 0
        self.debug_hitboxes: int = 0
        self.debug_resolution: Rect = Rect(0,0,0,0)
        # --- Asset References ---
        self.tileset: Optional[Tilemap] = None
        # self.animations: Dict = {}
        self.animation_variant_manager: AnimationVariantManager = AnimationVariantManager()
        self.dt = 0.0

    def create(self):
        """Initializes the game state, called once when the scene starts."""
        # print("TemplarScene: Creating...")
        
        # Load assets from the manager
        # self.tileset = self.assets.tileset("templar_data", "tileset")
        self.tileset = self.assets.tileset("templar_data", ("tilesetImage", "tilesetBoxes", "tilesetSolid"))
        if not self.tileset:
            raise Exception("Failed to load 'templar_data' tileset.")
        
        # self.tileset = self.assets.tilesets["templar"]

        # Load all animations and register variants
        all_animations = self.assets.animation("templar_data", "sprites")

        if all_animations and isinstance(all_animations, dict):
            for anim_name, animation in all_animations.items():
                if "Jumping" in anim_name:
                    animation.repeat = 0
                if anim_name.endswith('_flipped'):
                    base_name = anim_name[:-8]  # Remove '_flipped'
                    self.animation_variant_manager.register_variant(base_name, 'flipped', animation)
                else:
                    self.animation_variant_manager.register_variant(anim_name, 'normal', animation)

        # Or load individual animations
        # idle_anim = self.assets.get_animation("Idle")
        # idle_flipped_anim = self.assets.get_animation("Idle_flipped")

        # idle_normal = self.assets.animation("templar_data", [
        #     (sprites_Idle, 0, 0, 14, 13, 6, 12, 300),
        #     (sprites_Idle, 14, 0, 14, 12, 6, 11, 300),
        #     (sprites_Idle, 28, 0, 14, 12, 6, 11, 300)
        # ])

        # # For flipped Idle animation  
        # idle_flipped = self.assets.animation("templar_data", [
        #     (sprites_IdleH, 0, 0, 14, 13, 7, 12, 300),  # pivot_x = 14-1-6 = 7
        #     (sprites_IdleH, 14, 0, 14, 12, 7, 11, 300), # pivot_x = 14-1-6 = 7
        #     (sprites_IdleH, 28, 0, 14, 12, 7, 11, 300)  # pivot_x = 14-1-6 = 7
        # ])

        # self.animations = {
        #     # "Idle": self.assets.get_animation("Idle"),
        #     "Idle": self.assets.animation("templar_data", "Idle", "sprites"),
        #     "Running": self.assets.get_animation("Running"),
        #     "Jumping": self.assets.get_animation("Jumping"),
        #     "Hurt": self.assets.get_animation("Hurt"),
        #     "Victory": self.assets.get_animation("Victory")
        # }
        
        # Setup level
        from cpgame.game_assets.templar_data import room_level1 # Load specific room data
        flag_sequence = [(15, 13, 1), (19, 10, 2), (11, 6, 1), (5, 5, 1), (17, 2, 0), (1, 8, 0)]
        self.room = RoomEntity(WW, WH, 32, 224, self.tileset, flag_sequence) # type: ignore
        self.room.tiles = room_level1[2]
        self.room.compute_tile_collisions()

        # Setup player
        self.player = PlayerEntity()
        self.player.initialize(Vec2(self.room.spawn_x, self.room.spawn_y))
        self.player_set_stance(STANCE_IDLE)

        # Setup rendering state
        self.dirty_tiles = bytearray(self.room.w * self.room.h)
        for i in range(len(self.dirty_tiles)): self.dirty_tiles[i] = 1
        
        self.show_next_flags(1)

    def update(self, dt: float) -> Optional[str]:
        """Handles all game logic and input for one fixed-step update."""
        assert self.player and self.room and self.dirty_tiles is not None

        self.dt = dt

        # self.input.update() # Polls gint for the latest input state

        if self.input.exit:
            return "EXIT_GAME"
            # from cpgame.game_scenes.menu_scene import MenuScene
            # self.game.change_scene(MenuScene)
            # return
        
        dx = self.input.dx
        jump_down = keydown(KEY_SHIFT) or keydown(KEY_UP)
        if self.input.shift or self.input.up: self.player.jump_buffer = 3
        
        if keypressed(KEY_KBD):
            self.debug_hitboxes = (self.debug_hitboxes + 1) % 3
            # Mark all tiles dirty to redraw hitbox outlines
            for i in range(len(self.dirty_tiles)): self.dirty_tiles[i] = 1

        # --- Update Game State Timers ---
        self.game_time += dt
        self.player.anim.update(dt)

        # Update entities and remove finished ones
        self.entities = [e for e in self.entities if not e[1].update(dt)]

        if self.end_timer > 0:
            self.end_timer -= dt
            if self.end_timer <= 0: return "EXIT_GAME"
        
        if self.reset_timer > 0:
            self.reset_timer -= dt
            if self.reset_timer <= 0:
                self.reset_timer = -1
                self.player.initialize(Vec2(self.room.spawn_x, self.room.spawn_y))
                self.deaths += 1

        # --- Player Physics (Integer-based) ---
        if self.player.jump_buffer > 0: self.player.jump_buffer -= 1
        
        # Jumping
        if self.player.jump_buffer and self.player.grounded():
            self.player.speed.y = -140
            self.player.jump_frames = 5
            self.player.jump_buffer = 0

        # Horizontal Movement & Friction
        self.player.speed.x *= 0.97
        if self.input.dx > 0: self.player.speed.x = max(self.player.speed.x, 64)
        elif self.input.dx < 0: self.player.speed.x = min(self.player.speed.x, -64)
        else: self.player.speed.x //= 2 ## int(self.player.speed.x * 0.5)
        
        # Vertical Movement & Gravity
        if self.player.airborne(): self.player.speed.y += 9.81 * dt * 30
        if self.player.jump_frames > 0:
            # jump_down = keydown(KEY_SHIFT) or keydown(KEY_UP)
            if not jump_down: self.player.speed.y = max(self.player.speed.y, -20)
            self.player.jump_frames -= 1

        # Update facing direction and animation variants
        old_facing = self.player.facing
        if self.input.dx > 0: 
            self.player.facing = FACING_RIGHT
        elif self.input.dx < 0: 
            self.player.facing = FACING_LEFT
            
        # If facing changed, update animation variant
        # if old_facing != self.player.facing:
        self.player.anim.update_variant_states(flipped=(self.player.facing == FACING_LEFT))
        
        # Update stance (this will handle variant selection automatically)
        self.player_set_stance(STANCE_JUMPING if self.player.airborne() else 
                             (STANCE_RUNNING if self.input.dx else STANCE_IDLE))
        
        # self.player_set_stance(STANCE_JUMPING if self.player.airborne() else (STANCE_RUNNING if self.input.dx else STANCE_IDLE))
        # if self.input.dx > 0: self.player.facing = FACING_RIGHT
        # elif self.input.dx < 0: self.player.facing = FACING_LEFT

        # --- Collision and Displacement ---
        self.player.pos, self.physics_flags = self.physics_displace(self.player.pos, self.player.speed * dt) # type: ignore -- it is supported my __mul__
        self.player._grounded = (self.physics_flags & PH_GROUNDED) != 0

        # React to collision flags
        if self.physics_flags & (PH_LWALL | PH_RWALL): self.player.speed.x = 0
        if self.physics_flags & PH_HEADBANG: self.player.speed.y = max(self.player.speed.y, 0)
        if self.physics_flags & PH_GROUNDED: self.player.speed.y = 20 # Push gently into the ground

        # Check for death or out of bounds
        is_out_of_bounds = not (0 < self.player.pos.x < 16*self.room.w and 0 < self.player.pos.y < 16*self.room.h)
        if (self.physics_flags & PH_DEATH) or is_out_of_bounds:
            self.player_set_stance(STANCE_HURT)
            self.reset_timer = 0.6
        
        # Check for victory
        if self.flags_taken >= len(self.room.flag_sequence) and self.end_timer < 0:
            self.player_set_stance(STANCE_VICTORY)
            self.end_timer = 3.0
        return None

    def draw(self, frame_time_ms: int):
        """Renders the entire game world."""
        assert self.player and self.room and self.dirty_tiles is not None
        
        self.draw_room()
        for pos, entity_anim in self.entities:
            self.draw_entity(pos, entity_anim)
        self.draw_player()
        self.draw_hud(frame_time_ms)

        # Debug visualizations
        if self.debug_hitboxes >= 1:
            phb = self.physics_player_hitbox(self.player.pos)
            self.draw_outline(self.debug_resolution, C_RGB(0,31,0))
            self.draw_outline(phb, C_GREEN)
        if self.debug_hitboxes == 2:
            full_room_rect = Rect(0, 0, self.room.w << 4, self.room.h << 4)
            for b, bf, _ in self.room.hitboxesNear(full_room_rect):
                self.draw_flagged_outline(b, bf, C_RED, C_WHITE)

    # --- Scene-specific Helper Methods ---
    def player_set_stance(self, stance: int):
        assert self.player
        if self.player.stance == stance: return
        self.player.stance = stance
        
        # Determine base animation name
        base_anim_name = None
        if stance == STANCE_IDLE: base_anim_name = "Idle"
        elif stance == STANCE_RUNNING: base_anim_name = "Running"
        elif stance == STANCE_JUMPING: base_anim_name = "Jumping"
        elif stance == STANCE_HURT: base_anim_name = "Hurt"
        elif stance == STANCE_VICTORY: base_anim_name = "Victory"
        
        if base_anim_name:
            # Set base animation with variant manager - variant selection happens elsewhere
            self.player.anim.set_base_animation(base_anim_name, self.animation_variant_manager)
        
        # assert self.player
        # if self.player.stance == stance: return
        # self.player.stance = stance
        # if stance == STANCE_IDLE: self.player.anim.set(self.animations["Idle"])
        # elif stance == STANCE_RUNNING: self.player.anim.set(self.animations["Running"])
        # elif stance == STANCE_JUMPING: self.player.anim.set(self.animations["Jumping"])
        # elif stance == STANCE_HURT: self.player.anim.set(self.animations["Hurt"])
        # elif stance == STANCE_VICTORY: self.player.anim.set(self.animations["Victory"])

    def physics_player_hitbox(self, pos: Vec2) -> Rect:
        return Rect(pos.x - 5, pos.y - 14, 11, 14)

    def physics_acceptable(self, pos: Vec2) -> bool:
        assert self.room
        player_hb = self.physics_player_hitbox(pos)
        for hb, _, solid in self.room.hitboxesNear(player_hb):
            if solid == SOLID_STD and player_hb.intersects(hb):
                # HACK: Backwards world to tile grid conversion
                x, y = int(hb.x) >> 4, int(hb.y) >> 4
                # TODO: game.takeFlag(x, y)
                return False
        return True

    def physics_displace(self, pos: Vec2, diff: Vec2) -> Tuple[Vec2, int]:
        pr = self.physics_player_hitbox(pos + diff)
        resolution = Vec2(0, 0); flags = 0
        if self.room:
            for r, rf, solid in self.room.hitboxesNear(pr):
                if not pr.intersects(r): continue
                if solid == SOLID_DEATH: return pos + diff, PH_DEATH
                if solid in (SOLID_NOT, SOLID_FLAG): continue
                
                player_top_pixel = pos.y
                plank_top_pixel = r.top
                if solid == SOLID_PLANK and (diff.y < 0 or player_top_pixel > plank_top_pixel + 1): continue
                
                left_overlap = max(r.right - pr.left, 0)
                right_overlap = min(r.left - pr.right, 0)
                top_overlap = max(r.bottom - pr.top, 0)
                bottom_overlap = min(r.top - pr.bottom, 0)
                
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
    
    def mark_tiles_dirty(self, wr: Rect):
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
        if self.room.tiles:
            for ty in range(self.room.h):
                for tx in range(self.room.w):
                    t = self.room.tiles[i]
                    if t == 101 and self.flags_data.get((tx, ty), True): t = 0xff
                    if self.dirty_tiles and self.dirty_tiles[i]:
                        self.draw_tile(tx, ty, t)
                        self.dirty_tiles[i] = 0
                    i += 1
    
    def draw_tile(self, x: int, y: int, tileID: int):
        assert self.room
        assert self.tileset
        img = self.room.tileset.img # self.tileset.img ?
        sx, sy = MAP_X + 16 * x, MAP_Y + 16 * y
        w = img.width >> 4; tx, ty = tileID % w, tileID // w
        dsubimage(sx, sy, img, 176, 48, 16, 16) # background
        if 16 * ty < img.height:
            dsubimage(sx, sy, img, 16 * tx, 16 * ty, 16, 16)

    def draw_player(self):
        assert self.player
        p = self.player
        base = self.world2screen(p.pos)

        # Update animation state
        p.anim.update(self.dt)  # Assuming you have delta time
        
        # Draw current frame
        current_frame = p.anim.get_current_frame()
        if current_frame:
            draw_x = base.x - current_frame.pivot_x
            draw_y = base.y - current_frame.pivot_y
            dsubimage(draw_x, draw_y, 
                    current_frame.img, 
                    current_frame.src_x, current_frame.src_y,
                    current_frame.width, current_frame.height)
        
            self.mark_tiles_dirty(self.screen2world_rect(Rect(draw_x, draw_y, current_frame.width, current_frame.height)))

        # # base_x = (p.pos.x) + MAP_X
        # # base_y = (p.pos.y) + MAP_Y

        # if p.anim.index >= 0 and p.anim.frames:
        #     f = p.anim.frames[p.anim.index]
        #     img, cx = (f.imgH, f.w - 1 - f.cx) if flipped else (f.img, f.cx)
        #     draw_x, draw_y = base.x - cx, base.y - f.cy
        #     dsubimage(draw_x, draw_y, img, f.x, f.y, f.w, f.h)
        #     self.mark_tiles_dirty(self.screen2world_rect(Rect(draw_x, draw_y, f.w, f.h)))

    def draw_entity(self, pos: Vec2, anim: AnimationState):
        base = self.world2screen(pos)
        # base_x = (pos.x >> FIXED_POINT_SHIFT) + MAP_X
        # base_y = (pos.y >> FIXED_POINT_SHIFT) + MAP_Y
        if anim.index >= 0  and anim.frames:
            f = anim.frames[anim.index]
            draw_x, draw_y = base.x - f.cx, base.y - f.cy
            dsubimage(draw_x, draw_y, f.img, f.x, f.y, f.w, f.h)
            self.mark_tiles_dirty(self.screen2world_rect(Rect(draw_x, draw_y, f.w, f.h)))

    def draw_hud(self, frame_time_ms: int):
        x, y = HUD_X + 2, HUD_Y + 4
        drect(HUD_X, HUD_Y, HUD_X + HUD_W - 1, HUD_Y + HUD_H - 1, C_RGB(6,5,2))
        if self.debug_hitboxes > 0:
            dtext_opt(x, y+135, C_WHITE, C_NONE, DTEXT_LEFT, DTEXT_TOP, f"ft: {frame_time_ms} ms", -1)
        else:
            if self.room:
                dtext_opt(x, y, C_WHITE, C_NONE, DTEXT_LEFT, DTEXT_TOP, f"Flags: {self.flags_taken}/{len(self.room.flag_sequence)}", -1)
            dtext_opt(x, y+15, C_WHITE, C_NONE, DTEXT_LEFT, DTEXT_TOP, f"Deaths: {self.deaths}", -1)
            dtext_opt(x, y+30, C_WHITE, C_NONE, DTEXT_LEFT, DTEXT_TOP, f"Time: {self.game_time:.1f}", -1)

    def world2screen(self, pos: Vec2) -> Vec2:
        return Vec2(MAP_X + int(pos.x), MAP_Y + int(pos.y))
    def world2screen_rect(self, r: Rect) -> Rect:
        return Rect(MAP_X + int(r.x), MAP_Y + int(r.y), int(r.w), int(r.h))
    def screen2world_rect(self, r: Rect) -> Rect:
        return Rect(r.x - MAP_X, r.y - MAP_Y, r.w, r.h)
    
    def draw_outline(self, r: Rect, color: int):
        self.mark_tiles_dirty(r)
        r = self.world2screen_rect(r)
        drect_border(r.x, r.y, r.x+r.w-1, r.y+r.h-1, C_NONE, 1, color)
    
    def draw_flagged_outline(self, r: Rect, rb: int, c1: int, c2: int):
        self.mark_tiles_dirty(r)
        r = self.world2screen_rect(r)
        x1 = (r.x) + MAP_X
        y1 = (r.y) + MAP_Y
        x2 = ((r.x + r.w)) + MAP_X
        y2 = ((r.y + r.h)) + MAP_Y
        # dline(x1,y1,x2,y1, c2 if rb & PH_GROUNDED else c1)
        # dline(x1,y2,x2,y2, c2 if rb & PH_HEADBANG else c1)
        # dline(x1,y1,x1,y2, c2 if rb & PH_RWALL else c1)
        # dline(x2,y1,x2,y2, c2 if rb & PH_LWALL else c1)
        dline(r.x,r.y,r.x+r.w-1,r.y, c2 if rb & PH_GROUNDED else c1)
        dline(r.x,r.y+r.h-1,r.x+r.w-1,r.y+r.h-1, c2 if rb & PH_HEADBANG else c1)
        dline(r.x,r.y,r.x,r.y+r.h-1, c2 if rb & PH_RWALL else c1)
        dline(r.x+r.w-1,r.y,r.x+r.w-1,r.y+r.h-1, c2 if rb & PH_LWALL else c1)

