# scenes/templewa_scene.py
# A port of the "templewa" game into the cpgame engine structure.

from gint import *
try:
    from typing import Optional, List, Dict, Any, Tuple
    from cpgame.engine.game import Game
except:
    pass
import random

# Engine imports
from cpgame.engine.scene import Scene
from cpgame.engine.geometry import Vec2, Rect
from cpgame.engine.animation import AnimationState, AnimationVariantManager
from cpgame.engine.assets import Tilemap

# --- Constants & Configuration ---
FIXED_POINT_SHIFT = 8
WW, WH = 21, 15
MAP_X, MAP_Y = 0, 0
PLAYER_SPEED = 192 # Tuned for fixed-point math (3.0 in templewa * 64)
SKELETON_SPEED = 25 # (0.4 in templewa * 64)

# --- Ported Entity System from Templewa ---

class Entity:
    """Base class for all game objects."""
    def __init__(self, scene: 'TemplarScene'):
        self.scene = scene
        self.position = Vec2(0, 0)

    def update(self, dt: float): pass
    def draw(self): pass
    def gizmo(self): pass

class Collider:
    """A simple collider component using the engine's Rect."""
    def __init__(self):
        self.offset = Vec2(0, 0)
        self.size = Vec2(0, 0)

    def set(self, x: int, y: int, w: int, h: int):
        self.offset.x, self.offset.y = x, y
        self.size.x, self.size.y = w, h

    def get_rect(self, base_pos: Vec2) -> Rect:
        """Returns the world-space Rect of the collider."""
        return Rect(
            base_pos.x + self.offset.x,
            base_pos.y + self.offset.y,
            self.size.x,
            self.size.y
        )

    def gizmo(self, base_pos: Vec2):
        r = self.get_rect(base_pos)
        self.scene.draw_outline(r, C_RED)

class Character(Entity):
    """An entity with physics, collision, and animation."""
    def __init__(self, scene: 'TemplarScene'):
        super().__init__(scene)
        self.dir = 1  # 1 for right, -1 for left
        self.velocity = Vec2(0, 0)
        self.health = 100
        self.collider = Collider()
        self.grounded = False
        self.anim = AnimationState()

    def update(self, dt: float):
        self.update_physics(dt)

    def update_physics(self, dt: float):
        # Apply gravity (fixed-point value)
        self.velocity.y += 25

        # Move and collide with the world
        self.velocity, collision_flags = self.move_and_collide(self.velocity)

        # Update state based on collisions
        self.grounded = 'd' in collision_flags
        if 'd' in collision_flags or 'u' in collision_flags:
            self.velocity.y = 0
        if 'l' in collision_flags or 'r' in collision_flags:
            self.velocity.x = 0

    def get_hitbox(self) -> Rect:
        """Returns the collider's Rect in world space (fixed-point)."""
        return self.collider.get_rect(self.position)

    def move_and_collide(self, vel: Vec2) -> Tuple[Vec2, str]:
        """
        Moves the character by velocity, handling collisions with tiles.
        Returns the adjusted velocity and collision flags ('u', 'd', 'l', 'r').
        """
        collision_flags = ""
        
        # Move X
        self.position.x += vel.x
        hitbox = self.get_hitbox()
        for tile_rect in self.scene.get_solid_tiles_near(hitbox):
            if hitbox.overlaps(tile_rect):
                if vel.x > 0:
                    hitbox.x = tile_rect.x - hitbox.w
                    collision_flags += 'r'
                elif vel.x < 0:
                    hitbox.x = tile_rect.x + tile_rect.w
                    collision_flags += 'l'
                self.position.x = hitbox.x - self.collider.offset.x
                vel.x = 0

        # Move Y
        self.position.y += vel.y
        hitbox = self.get_hitbox()
        for tile_rect in self.scene.get_solid_tiles_near(hitbox):
            if hitbox.overlaps(tile_rect):
                if vel.y > 0:
                    hitbox.y = tile_rect.y - hitbox.h
                    collision_flags += 'd'
                elif vel.y < 0:
                    hitbox.y = tile_rect.y + tile_rect.h
                    collision_flags += 'u'
                self.position.y = hitbox.y - self.collider.offset.y
                vel.y = 0

        return vel, collision_flags

    def draw(self):
        current_frame = self.anim.get_current_frame()
        if not current_frame:
            return

        # Calculate draw position from world position (fixed-point) and pivot
        draw_x = (self.position.x >> FIXED_POINT_SHIFT) + MAP_X - current_frame.pivot_x
        draw_y = (self.position.y >> FIXED_POINT_SHIFT) + MAP_Y - current_frame.pivot_y
        
        dsubimage(
            draw_x, draw_y,
            current_frame.img,
            current_frame.src_x, current_frame.src_y,
            current_frame.width, current_frame.height
        )
    
    def gizmo(self):
        self.collider.gizmo(self.position)

class Player(Character):
    def __init__(self, scene: 'TemplarScene'):
        super().__init__(scene)
        self.state = "idle"
        self.collider.set(6 << FIXED_POINT_SHIFT, 4 << FIXED_POINT_SHIFT, 16 << FIXED_POINT_SHIFT, 28 << FIXED_POINT_SHIFT)

    def set_state(self, new_state: str):
        if self.state == new_state:
            return
        self.state = new_state
        
        anim_map = {
            "idle": "Idle", "run": "Running", "jump": "Jumping",
            "fall": "Jumping", "attack": "Attack"
        }
        self.anim.set_base_animation(anim_map.get(self.state, "Idle"), self.scene.animation_variant_manager)

    def update(self, dt: float):
        # --- State Logic ---
        # Fall detection
        if self.velocity.y > (1 << FIXED_POINT_SHIFT):
            self.set_state("fall")

        # Jumping
        if self.scene.input.shift and self.grounded:
            self.velocity.y = - (4 << FIXED_POINT_SHIFT) # Jump velocity
            self.set_state("jump")

        # Horizontal movement
        dx = self.scene.input.dx
        if self.state in ["idle", "run", "fall", "jump"]:
            if dx != 0:
                self.velocity.x = dx * PLAYER_SPEED
                self.dir = 1 if dx > 0 else -1
                if self.grounded:
                    self.set_state("run")
            elif self.grounded:
                self.velocity.x = 0
                self.set_state("idle")
        
        # Grounded check
        if self.state in ["jump", "fall"] and self.grounded:
            self.set_state("idle")

        # Update animation direction
        self.anim.update_variant_states(flipped=(self.dir == -1))
        self.anim.update(dt)

        # --- Physics ---
        super().update_physics(dt)

class Skeleton(Character):
    def __init__(self, scene: 'TemplarScene', start_node: int):
        super().__init__(scene)
        self.collider.set(0, 0, 16 << FIXED_POINT_SHIFT, 32 << FIXED_POINT_SHIFT)
        self.target_node = start_node
        self.state = "walk"
        self.anim.set_base_animation("Running", self.scene.animation_variant_manager)
        
        start_pos = self.scene.graph['nodes'][self.target_node]
        self.position.x = start_pos[0] * 16 << FIXED_POINT_SHIFT
        self.position.y = (start_pos[1] * 16 - 16) << FIXED_POINT_SHIFT
    
    def update(self, dt: float):
        if self.target_node is None:
            self.velocity.x = 0
            return

        # Simple pathfinding from templewa
        target_pos = self.scene.graph['nodes'][self.target_node]
        target_x = target_pos[0] * 16 << FIXED_POINT_SHIFT
        target_y = (target_pos[1] * 16 - 16) << FIXED_POINT_SHIFT
        
        dx = target_x - self.position.x
        dy = target_y - self.position.y

        # Check if node is reached
        if abs(dx) < (4 << FIXED_POINT_SHIFT) and abs(dy) < (6 << FIXED_POINT_SHIFT):
            next_nodes = self.scene.graph['edges'][self.target_node]
            if next_nodes:
                self.target_node = random.choice(next_nodes)
            else:
                self.target_node = None
        else:
            # Move towards target
            self.dir = 1 if dx > 0 else -1
            self.velocity.x = self.dir * SKELETON_SPEED
        
        self.anim.update_variant_states(flipped=(self.dir == -1))
        self.anim.update(dt)
        super().update_physics(dt)

class Crystal(Entity):
    def __init__(self, scene: 'TemplarScene'):
        super().__init__(scene)
        self.anim_time = 0
        self.anim = AnimationState()
        bounce_anim = scene.assets.animation('templar_data', 'bounce')
        if bounce_anim:
            self.anim.set_animation(bounce_anim.get(None))

    def update(self, dt: float):
        self.anim.update(dt)

    def draw(self):
        current_frame = self.anim.get_current_frame()
        if not current_frame:
            return

        # Bobbing effect
        bob_offset = int(self.anim_time * 10) % 12
        bob_y = bob_offset if bob_offset < 6 else 12 - bob_offset

        draw_x = (self.position.x >> FIXED_POINT_SHIFT) + MAP_X - current_frame.pivot_x
        draw_y = (self.position.y >> FIXED_POINT_SHIFT) + MAP_Y - current_frame.pivot_y - (bob_y // 2)

        dsubimage(
            draw_x, draw_y,
            current_frame.img,
            current_frame.src_x, current_frame.src_y,
            current_frame.width, current_frame.height
        )


class TemplewaScene(Scene):
    """The main scene for the Templewa game port."""
    def create(self):
        self.camera = Vec2(0, 0)
        self.entities: List[Entity] = []

        # Load assets
        self.tileset: Optional[Tilemap] = self.assets.tileset("templar_data", "tileset")
        all_anims = self.assets.animation("templar_data", "sprites")
        self.animation_variant_manager = AnimationVariantManager()
        if all_anims and isinstance(all_anims, dict):
            for name, anim in all_anims.items():
                if name.endswith("_flipped"):
                    self.animation_variant_manager.register_variant(name[:-8], 'flipped', anim)
                else:
                    self.animation_variant_manager.register_variant(name, 'normal', anim)

        # Load map data (using templar_data room)
        from cpgame.game_assets.templar_data import room_level1
        self.map_w, self.map_h, self.map_tiles = room_level1
        
        # Load graph data (from templewa's game_map.py)
        self.graph = {
            'nodes': [[33, 6], [30, 3], [39, 6], [42, 9], [8, 3], [7, 7], [10, 10], [15, 10], [15, 16], [19, 12], [46, 9], [46, 12], [49, 8], [49, 12], [52, 8], [54, 6], [60, 6], [63, 3], [72, 3], [72, 12], [60, 12], [60, 17], [55, 12], [8, 8], [4, 7], [7, 16], [5, 18], [4, 18], [4, 22], [10, 22], [11, 23], [12, 23], [12, 26], [11, 19], [19, 19], [30, 26], [33, 23], [41, 23], [44, 26], [36, 23], [38, 23], [51, 26], [55, 22], [67, 17], [67, 22], [68, 22], [68, 26], [66, 26], [63, 29], [60, 29], [60, 33], [65, 33], [65, 37], [70, 35], [67, 35], [8, 26], [5, 29], [4, 29], [4, 32], [5, 32], [6, 33], [7, 33], [8, 35], [6, 37], [4, 37], [19, 35], [21, 37], [23, 37], [4, 40], [23, 40], [35, 40], [39, 36], [46, 36], [46, 38], [48, 38], [48, 40], [56, 40], [59, 37], [36, 6], [7, 36], [68, 3], [2, 32], [72, 19], [70, 19], [70, 26], [37, 31], [42, 31], [32, 31], [32, 35], [33, 36], [36, 36], [36, 39], [42, 36], [54, 30], [57, 30], [13, 35], [2, 20]],
            'edges': [[1], [4], [3], [10], [23], [24], [7], [8], [25], [8], [11], [9, 13], [13], [22], [12], [14], [15], [16], [18], [20], [21], [43], [21], [5, 6], [], [26], [27], [28], [29], [30], [31], [32], [33], [55, 35], [30], [36], [39], [38], [40], [37], [], [], [41], [42], [44], [45, 42], [46], [47], [48], [49], [50], [51], [52], [54], [], [53], [56], [57], [58], [59], [60], [61], [79], [95], [64], [68], [66], [67], [69], [69], [70], [91], [92], [73], [74], [75], [76], [77], [52], [0, 2], [63, 62], [17, 18], [58], [83], [84], [46], [87, 86], [92], [88], [89], [90], [91], [71], [72], [94], [50], [65], [28]]
        }
        spawnable_nodes = [78,80,34,81,95,85,93,82,96]

        # Create Player
        self.player = Player(self)
        self.player.position = Vec2(100 << FIXED_POINT_SHIFT, 100 << FIXED_POINT_SHIFT)
        self.entities.append(self.player)

        # Create other entities
        self.entities.append(Crystal(self))
        self.entities[-1].position = Vec2(200 << FIXED_POINT_SHIFT, 150 << FIXED_POINT_SHIFT)
        
        for _ in range(5):
            self.entities.append(Skeleton(self, random.choice(spawnable_nodes)))

    def update(self, dt: float):
        for entity in self.entities:
            entity.update(dt)
        
        # Camera follows player
        cam_target_x = (self.player.position.x >> FIXED_POINT_SHIFT) - DWIDTH // 2
        cam_target_y = (self.player.position.y >> FIXED_POINT_SHIFT) - DHEIGHT // 2
        self.camera.x += (cam_target_x - self.camera.x) // 8
        self.camera.y += (cam_target_y - self.camera.y) // 8


    def draw(self, frame_time_ms: int):
        dclear(C_BLACK)
        self.draw_map()
        for entity in self.entities:
            entity.draw()

    def draw_map(self):
        if not self.tileset: return
        
        tile_size = 16
        cam_x, cam_y = self.camera.x, self.camera.y
        
        x_start = max(0, cam_x // tile_size)
        y_start = max(0, cam_y // tile_size)
        x_end = min(self.map_w, (cam_x + DWIDTH) // tile_size + 1)
        y_end = min(self.map_h, (cam_y + DHEIGHT) // tile_size + 1)
        
        img = self.tileset.img
        img_w_tiles = img.width // tile_size

        for ty in range(y_start, y_end):
            for tx in range(x_start, x_end):
                tile_id = self.map_tiles[ty * self.map_w + tx]
                if tile_id == 0xff: continue

                draw_x = tx * tile_size - cam_x
                draw_y = ty * tile_size - cam_y
                
                tile_sx = (tile_id % img_w_tiles) * tile_size
                tile_sy = (tile_id // img_w_tiles) * tile_size
                
                dsubimage(draw_x, draw_y, img, tile_sx, tile_sy, tile_size, tile_size)

    def get_solid_tiles_near(self, hitbox: Rect) -> List[Rect]:
        """Returns a list of solid tile rectangles near a given hitbox."""
        if not self.tileset: return []
        
        solid_rects = []
        tile_size = 16
        
        # Convert fixed-point hitbox to tile coordinates
        tx_start = max(0, (hitbox.x >> FIXED_POINT_SHIFT) // tile_size)
        ty_start = max(0, (hitbox.y >> FIXED_POINT_SHIFT) // tile_size)
        tx_end = min(self.map_w - 1, ((hitbox.x + hitbox.w) >> FIXED_POINT_SHIFT) // tile_size)
        ty_end = min(self.map_h - 1, ((hitbox.y + hitbox.h) >> FIXED_POINT_SHIFT) // tile_size)

        for ty in range(ty_start, ty_end + 1):
            for tx in range(tx_start, tx_end + 1):
                tile_id = self.map_tiles[ty * self.map_w + tx]
                if tile_id != 0xff and tile_id in self.tileset.solid:
                    solid_rects.append(Rect(
                        tx * tile_size << FIXED_POINT_SHIFT,
                        ty * tile_size << FIXED_POINT_SHIFT,
                        tile_size << FIXED_POINT_SHIFT,
                        tile_size << FIXED_POINT_SHIFT
                    ))
        return solid_rects
        
    def draw_outline(self, r_fp: Rect, color: int):
        """Draws an outline for a fixed-point Rect."""
        r_screen = Rect(
            (r_fp.x >> FIXED_POINT_SHIFT) - self.camera.x,
            (r_fp.y >> FIXED_POINT_SHIFT) - self.camera.y,
            r_fp.w >> FIXED_POINT_SHIFT,
            r_fp.h >> FIXED_POINT_SHIFT
        )
        drect_border(r_screen.x, r_screen.y, r_screen.x + r_screen.w, r_screen.y + r_screen.h, C_NONE, 1, color)