# cpgame/game_scenes/templewa_scene.py
# A complete and faithful port of the "templewa" game into a cpgame scene.

from gint import *
try:
    from typing import Optional, List, Dict, Any, Tuple, Set
    from cpgame.engine.game import Game
except:
    pass
import random
import time
import sys

# Engine imports
from cpgame.engine.scene import Scene
from cpgame.engine.geometry import Vec2, VecF2

# Asset and data import
from cpgame.game_assets import templewa_data
from micropython import const

DH = const(240)
DW = const(320)

class GameTimer:
    """Manages the delta time and speed compensation from game_time.py."""
    def __init__(self):
        self.delta = 0.0
        self.last_time = time.time()
        self.base_time = 0.015

    def reset(self):
        self.delta = 0.0
        self.last_time = time.time()

    def update(self, dt: float):
        # TODO: use dt
        current_time = time.time()
        self.delta = current_time - self.last_time
        self.last_time = current_time

    def speed_compensation(self) -> float:
        compensation = self.delta / self.base_time
        # This unique formula is preserved from the original
        compensation = (compensation / 2) - int(compensation) + 1
        return max(1.0, compensation)

    def repeat_loop(self) -> int:
        return int(max(1.0, self.delta / self.base_time))

class GameMap:
    """Game Map"""
    def __init__(self, width: int, height: int, data: List[int]):
        self.width = width
        self.height = height
        
        if data is not None:
            self.tiles = data
        
        self.tile_size = 16
        self.edited: Set[Tuple[int, int]] = set()

    def get(self, x: int, y: int) -> int:
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y * self.width + x]
        return -1 # Out of bounds

    def add_refresh(self, x: int, y: int):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.edited.add((x, y))

class Graph:
    """Graph"""
    def __init__(self, nodes: List, edges: List):
        self.nodes = nodes
        self.edges = edges

    def next(self, node_idx: int) -> Optional[int]:
        if node_idx < len(self.nodes) and self.edges[node_idx]:
            return random.choice(self.edges[node_idx])
        return None

class Entity:
    def __init__(self, scene: 'TemplewaScene'):
        self.scene = scene
        self.position = VecF2(0, 0) # TODO: vec2

    def update(self): pass
    def draw(self): pass
    def draw_outside(self): pass
    def _debug_hitbox(self): pass

class Collider:
    def __init__(self):
        self.offset = [0, 0]
        self.size = [0, 0]

    def set(self, x: int, y: int, w: int, h: int):
        self.offset = [x, y]
        self.size = [w, h]

    def _debug_hitbox(self, scene: 'TemplewaScene', x: int, y: int):
        x = x + self.offset[0] - scene.camera.x
        y = y + self.offset[1] - scene.camera.y
        drect_border(x, y, x + self.size[0], y + self.size[1], C_NONE, 1, C_RED)

class Character(Entity):
    COLLIDER_IDS = {0, 1, 5, 10, 11, 47, 48, 46, 49}
    COLLIDER_IGNORE = {46, 47, 48, 49}

    def __init__(self, scene: 'TemplewaScene'):
        super().__init__(scene)
        self.dir = 1
        self.velocity = VecF2(0.0, 0.0)
        self.acceleration = VecF2(0.0, 0.0)
        self.health = 100
        self.attack_power = 10
        self.defense = 5
        self.speed = 1.0
        self.collider = Collider()
        self.grounded = False

    def _debug_hitbox(self):
        self.collider._debug_hitbox(self.scene, int(self.position.x), int(self.position.y))

    def update(self):
        self.update_physics()

    def update_physics(self):
        self.acceleration.y += 0.1 # Gravity effect
        # Update the position based on velocity and acceleration
        x = self.velocity.x + 0.5 * self.acceleration.x
        y = self.velocity.y + 0.5 * self.acceleration.y
        self.velocity.x += self.acceleration.x
        self.velocity.y += self.acceleration.y
        self.want_to(self.position.x + x, self.position.y + y)
        self.acceleration.x = 0.0
        self.acceleration.y = 0.0

    def detect_collision(self, p1: Tuple[float, float], p2: Tuple[float, float]) -> Optional[Tuple[int, int, int]]:
        x_st = int(p1[0] // self.scene.map.tile_size)
        y_st = int(p1[1] // self.scene.map.tile_size)
        x_end = int(p2[0] // self.scene.map.tile_size)
        y_end = int(p2[1] // self.scene.map.tile_size)
        detected = None
        for i in range(max(0, x_st), min(self.scene.map.width, x_end + 1)):
            for j in range(max(0, y_st), min(self.scene.map.height, y_end + 1)):
                tile_id = self.scene.map.get(i, j)
                if tile_id in self.COLLIDER_IDS:
                    detected = (i, j, tile_id)
                    if tile_id not in self.COLLIDER_IGNORE:
                        return detected
        return detected

    def _tl_br(self, x: float, y: float) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        tl = (x + self.collider.offset[0], y + 1 + self.collider.offset[1])
        br = (x + self.collider.offset[0] + self.collider.size[0], y + self.collider.offset[1] + self.collider.size[1])
        return tl, br

    def want_to(self, x: float, y: float):
        self.grounded = False
        tl, br = self._tl_br(x, y)
        res = self.detect_collision(tl, br)
        if res is not None:
            if res[2] not in self.COLLIDER_IGNORE:
                x = self.position.x
                tl, br = self._tl_br(x, y)
            self.velocity.x = 0
            bas = self.detect_collision((tl[0], br[1]), (br[0], br[1]))
            if bas is not None:
                ajuste = 0
                tempY = y
                stair = False
                tile_size = self.scene.map.tile_size
                if bas[2] == 46 and int(tl[0] // tile_size) == bas[0]:
                    ajuste = int(tl[0]) % tile_size
                    stair = True
                elif bas[2] == 49 and int(br[0] // tile_size) == bas[0]:
                    ajuste = tile_size - (int(br[0]) % tile_size)
                    stair = True

                if ajuste <= (self.speed * self.scene.timer.speed_compensation()) + 0.1:
                    ajuste = 0
                
                y = (bas[1] * tile_size) - self.collider.offset[1] - self.collider.size[1] - 1 + ajuste
                if stair and tempY < y:
                    y = tempY
                else:
                    self.grounded = True
                    self.velocity.y = 0
                tl, br = self._tl_br(x, y)

            haut = self.detect_collision((tl[0], tl[1]), (br[0], tl[1]))
            if haut is not None:
                y = self.position.y + 1
                self.velocity.y = 0
        
        self.position.x = x
        self.position.y = y

class Player(Character):
    def __init__(self, scene: 'TemplewaScene'):
        super().__init__(scene)
        self.animation = 0
        self.states_anim = [[0,2, 0.1],[3,8, 0.2],[9,14, 0.2],[14,15, 0.2],[0,4, 0.4]]
        self.state = 0
        self.change_state(0)
        self.speed = 3.0
        self.collider.set(6, 0+4, 16, 32-4)
        self.smoothX = 0

        self.can_attack: List[Skeleton] = []
        self.attack_power = 40

    def change_state(self, state: int):
        if state != self.state:
            self.state = state
            self.animation = self.states_anim[state][0]

    def attack(self):
        for entity in self.can_attack[:]: # Iterate over a copy
            if self.position.x < entity.position.x and self.dir == 1:
                entity.take_damage(self.attack_power)
            elif self.position.x > entity.position.x and self.dir == -1:
                entity.take_damage(self.attack_power)

    def update(self):
        super().update()
        speed = self.speed * self.scene.timer.speed_compensation()
        
        if self.velocity.y > 1:
            self.change_state(3)

        if self.state <= 1: # IDLE or RUN
            if self.scene.input.is_trigger('cancel'): # shift
                self.change_state(4)
                self.attack()
            
            elif self.scene.input.is_repeat('up'): # Alpha
                tl, br = self._tl_br(self.position.x, self.position.y - 1)
                up = self.detect_collision(
                    (tl[0],tl[1]-4),
                    (br[0],tl[1]-4)
                )

                if up is None or up[2] in (47, 48): # TODO: use tilemap collider id
                    self.acceleration.y = -self.speed * 1.25
                    if self.scene.input.is_repeat('left'):
                        self.velocity.x = -speed
                    elif self.scene.input.is_repeat('right'):
                        self.velocity.x = speed
                
                self.velocity.x /= 1.75
                self.change_state(2)
            
            elif self.scene.input.is_repeat('left'):
                if self.smoothX > 0:
                    self.smoothX = 0
                
                self.dir = -1
                self.change_state(1)

                if abs(self.smoothX) < speed:
                    self.smoothX += -speed/8
                self.velocity.x = self.smoothX
            
            elif self.scene.input.is_repeat('right'):
                if self.smoothX < 0:
                    self.smoothX = 0
                
                self.dir = 1
                self.change_state(1)
                
                if abs(self.smoothX) < speed:
                    self.smoothX += speed/8
                self.velocity.x = self.smoothX
            
            else:
                self.change_state(0)
                self.velocity.x = 0

        elif self.state in [2, 3]: # JUMP or FALL
            if self.grounded:
                self.change_state(0)
            if self.state == 2 and int(self.animation) >= self.states_anim[self.state][1]:
                self.change_state(3)
            
            if self.scene.input.is_repeat('left'):
                self.dir = -1
                if abs(self.velocity.x) < 0.2:
                    self.velocity.x = -0.2
                elif self.velocity.x > 0:
                    self.velocity.x /= 1.05
            
            if self.scene.input.is_repeat('right'):
                self.dir = 1
                if abs(self.velocity.x) < 0.2:
                    self.velocity.x = 0.2
                elif self.velocity.x < 0:
                    self.velocity.x /= 1.05

        elif self.state == 4: # ATTACK
            if int(self.animation) >= self.states_anim[self.state][1]:
                self.change_state(0)
        
        if self.state != 1:
            self.smoothX = 0
        
    def draw(self):
        self.animation += self.states_anim[self.state][2] * self.scene.timer.speed_compensation() * self.scene.timer.repeat_loop()
        index = int(self.animation)
        if index > self.states_anim[self.state][1]:
            self.animation = float(self.states_anim[self.state][0])
            index = self.states_anim[self.state][0]

        cam_x, cam_y = self.scene.camera.items()
        pos_x, pos_y = int(self.position.x - cam_x), int(self.position.y - cam_y)

        if self.state == 4:
            img = templewa_data.player_attack
            y_offset = 0 if self.dir == 1 else 50
            x_offset = 2 if self.dir == 1 else -18
            self.scene.draw_subimage(pos_x + x_offset, pos_y - 18, img, 50 * index, y_offset, 50, 50)
        else:
            img = templewa_data.player_basic
            y_offset = 0 if self.dir == 1 else 32
            self.scene.draw_subimage(pos_x, pos_y, img, 32 * index, y_offset, 32, 32)

class Skeleton(Character):
    def __init__(self, scene: 'TemplewaScene', node: int):
        super().__init__(scene)
        
        self.animation = 0
        # [start, end, speed, sx, sw, sheet_idx, (dx, dy), inv_dx]
        self.states_anim = [ # TODO: use engine Animation + AnimationFrame class
            [0,4, 0.1,0,22,0,(0,0),-5],
            [0,2, 0.2,110,30,0,(-5,0),-8],
            [0,2, 0.1,200,33,0,(-8,0),-8],
            [0,6,0.2,0,43,1,(-5,-4),-21]
        ]
        self.state = 0
        self.position.x = 20
        self.position.y = 40
        self.change_state(0)
        self.speed = 0.4
        self.collider.set(0, 0, 16, 32)
        self.dir = 1
        self.attack_power = 5

        self.target_node = node
        self.can_attack = False
        self.grounded = False
        self.touched = False
        self.cooldown = 0
        self.cooldown_wait = 5
    
    def change_state(self, state: int):
        # TODO: use animation states
        if state != self.state:
            self.cooldown = self.cooldown_wait
            self.state = state
            self.animation = self.states_anim[state][0]
    
    def take_damage(self, damage: int):
        self.health -= damage
        if self.health <= 0:
            self.change_state(2)
        else:
            self.change_state(1)

    def detect_player(self):
        player = self.scene.player
        if self.grounded and abs(self.position.x - 8 - player.position.x) < 32 and abs(self.position.y - player.position.y) < 16:
            if not self.can_attack:
                self.can_attack = True
                player.can_attack.append(self)
            
            if self.position.x < player.position.x:
                self.dir = 1
            else:
                self.dir = -1
            
            self.change_state(3)
        elif self.can_attack:
            self.can_attack = False
            player.can_attack.remove(self)
        return self.can_attack

    def update(self):
        if self.state in [1, 2]: # HIT or DEATH
            return

        if self.health <= 0:
            self.scene.to_remove_entities.append(self)
            return

        # super().update()
        
        if self.state == 3 and int(self.animation) == 3:
            if not self.touched:
                if self.can_attack:
                    self.scene.change_life(self.scene.player.health - self.attack_power)
                elif self.target_node is None:
                    self.scene.change_crystal(self.scene.crystal_hp - 1)
            self.touched = True
        else:
            self.touched = False
        
        if self.detect_player():
            # self.velocity = VecF2(0,0) # Stop when attacking
            return

        if self.target_node is None:
            self.change_state(3)
            # self.velocity = VecF2(0,0)
            return

        self.grounded = True
        compensation = self.scene.timer.speed_compensation()

        pos = self.scene.graph.nodes[self.target_node]
        target_pos = (pos[0] * self.scene.map.tile_size, pos[1] * self.scene.map.tile_size - 16)
        
        if abs(self.position.x - target_pos[0]) <= 4:
            self.position.x = target_pos[0]
            if abs(self.position.y - target_pos[1]) <= 6:
                self.position.y = target_pos[1]
                self.target_node = self.scene.graph.next(self.target_node)
                return
            else:
                if self.position.y < target_pos[1]:
                    self.position.y += 1.5 * compensation 
                    self.grounded = False
                else:
                    self.position.y = target_pos[0]
        else:
            if abs(self.position.y - target_pos[1]) > 4:
                if self.position.y < target_pos[1]:
                    self.position.y += self.speed * compensation
                else:
                    self.position.y -= self.speed * compensation
            
            if self.position.x < target_pos[0]:
                self.dir = 1
                self.change_state(0)
                self.position.x += self.speed * compensation
            
            elif self.position.x > target_pos[0]:
                self.dir = -1
                self.change_state(0)
                self.position.x -= self.speed * compensation

    def draw(self):
        # Animation logic
        next_anim = True
        if self.state == 3 and self.cooldown > 0:
            self.cooldown -= 1
            next_anim = False
        else:
            self.cooldown = self.cooldown_wait

        if next_anim:
            self.animation += min(1,
                self.states_anim[self.state][2] * self.scene.timer.speed_compensation() * self.scene.timer.repeat_loop()
            )

        index = int(self.animation)
        if index > self.states_anim[self.state][1]:
            self.animation = float(self.states_anim[self.state][0])
            index = self.states_anim[self.state][0]
            if self.state == 3:
                self.cooldown = self.cooldown_wait
            if self.state == 1:
                self.change_state(0)
                return
        
        # Drawing
        cam_x, cam_y = self.scene.camera.items()
        pos_x, pos_y = int(self.position.x - cam_x), int(self.position.y - cam_y)
        
        state_info = self.states_anim[self.state]
        # TODO: use assets loader
        img = templewa_data.skeleton_basic if state_info[5] == 0 else templewa_data.skeleton_attack
        sy = 0 if self.dir == 1 else img.height // 2
        
        dx, dy = state_info[6]
        
        if self.dir == -1:
            dx = state_info[7]
        
        sx, sw, sh = state_info[3] + state_info[4] * index, state_info[4], int(img.height // 2)
        
        self.scene.draw_subimage(pos_x + dx, pos_y + dy, img, sx, sy, sw, sh)
    
    def draw_outside(self):
        # return super().draw_outside()
        next_anim = True
        if self.state == 3:
            if self.cooldown > 0:
                self.cooldown -= 1
                next_anim = False
        else:
            self.cooldown = self.cooldown_wait
        
        state_info = self.states_anim[self.state]

        if next_anim:
            self.animation += min(1,
                state_info[2] * self.scene.timer.speed_compensation() * self.scene.timer.repeat_loop()
            )
        
        index = int(self.animation)
        if index > state_info[1]:
            self.animation = state_info[0]
            index = state_info[0]
            if self.state == 3:
                self.cooldown = self.cooldown_wait
            if self.state == 1 or self.state == 2:
                self.change_state(0)

class Crystal(Entity):
    def __init__(self, scene: 'TemplewaScene'):
        super().__init__(scene)
        self.anim = 0.0

    def draw(self):
        self.anim += min(1, 0.1 * self.scene.timer.speed_compensation() * self.scene.timer.repeat_loop())
        
        if self.anim > 12:
            self.anim = 0
        
        temp = self.anim if self.anim < 6 else 12 - self.anim
        
        cam_x, cam_y = self.scene.camera.items()
        pos_x, pos_y = int(self.position.x - cam_x), int(self.position.y - cam_y)
        
        self.scene.draw_subimage(pos_x, pos_y - temp, templewa_data.crystal, 0, 0, templewa_data.crystal.width, templewa_data.crystal.height)

class TemplewaScene(Scene):
    """The main scene that runs the Templewa game."""
    
    def create(self):
        # Game State
        self.state = 'menu' # 'menu', 'playing', 'paused', 'gameover'
        self.camera = Vec2(0, 0)
        self.crystal_hp = 100
        self.to_remove_entities: List[Entity] = []
        self.to_draw_calls = []
        self.menu_idx = 0
        self.pause_idx = 0
        self.debug_mode = False
        
        # Systems and Data
        self.timer = GameTimer()
        self.map = GameMap(75, 42, templewa_data.map_data)
        self.graph = Graph(templewa_data.graph_data['nodes'], templewa_data.graph_data['edges'])
        
        # Initialize Game World
        self.init_game_world()
        self.draw_map_full()

    def init_game_world(self):
        """Sets up the player, enemies, and crystals for a new game."""
        self.entities: List[Entity] = []
        
        self.player = Player(self)
        self.player.position = VecF2(580, 350)
        self.entities.append(self.player)
        
        # Crystals
        crystal1 = Crystal(self)
        crystal1.position = VecF2(596, 312)
        self.entities.append(crystal1)
        
        crystal2 = Crystal(self)
        crystal2.position = VecF2(52, 52)
        self.entities.append(crystal2)
        
        crystal3 = Crystal(self)
        crystal3.position = VecF2(1140, 500)
        self.entities.append(crystal3)

        self.move_camera(25 * 16, 14 * 16)
        self.crystal_hp = 100

        # Initial Skeletons
        for _ in range(8):
            self.spawn_skeleton()
            for j in range(20):
                self.update(0.0)
        

    def update(self, dt: float):

        if self.input.is_trigger('debug'): # Toggle debug mode
            self.debug_mode = not self.debug_mode
            self.draw_map_full() # Force display hitboxes
            
        self.timer.update(dt)

        if self.state == 'menu':
            if self.input.is_trigger('up'): self.menu_idx = 0
            if self.input.is_trigger('down'): self.menu_idx = 1
            if self.input.is_trigger('confirm'):
                if self.menu_idx == 0:
                    self.state = 'playing'
                    self.init_game_world()
                else: return "EXIT_GAME"
        
        elif self.state == 'playing':
            if self.input.is_trigger('page_up'): # MENU key
                self.state = 'paused'
                self.pause_idx = 0
                return

            for _ in range(self.timer.repeat_loop()):
                for entity in self.entities:
                    entity.update()
                
                for entity in self.to_remove_entities:
                    if entity in self.entities:
                        self.entities.remove(entity)
                        self.spawn_skeleton()
                self.to_remove_entities.clear()

            # Camera follow
            if (self.player.position.x - self.camera.x) < -18:
                self.move_camera(self.camera.x - 25 * self.map.tile_size, self.camera.y)
            if (self.player.position.x - self.camera.x) > DH-14:
                self.move_camera(self.camera.x + 25 * self.map.tile_size, self.camera.y)
            if (self.player.position.y - self.camera.y) < -18:
                self.move_camera(self.camera.x, self.camera.y - 14 * self.map.tile_size)
            if (self.player.position.y - self.camera.y) > DH-14:
                self.move_camera(self.camera.x, self.camera.y + 14 * self.map.tile_size)
            # self.camera.x = self.player.position.x - DW / 2
            # self.camera.y = self.player.position.y - DH / 2

            if self.player.health <= 0 or self.crystal_hp <= 0:
                self.state = 'gameover'
        
        elif self.state == 'paused':
            if self.input.is_trigger('up'): self.pause_idx = 0
            if self.input.is_trigger('down'): self.pause_idx = 1
            if self.input.is_trigger('cancel') or (self.input.is_trigger('confirm') and self.pause_idx == 0):
                self.state = 'playing'
                self.draw_map_full()
            if self.input.is_trigger('confirm') and self.pause_idx == 1:
                return "EXIT_GAME"
        
        elif self.state == 'gameover':
            if self.input.is_trigger('confirm'):
                self.state = 'menu'
        return None

    def draw(self, frame_time_ms: int):
        if self.state == 'menu':
            self.draw_panel(Vec2(96, 110),Vec2(224, 190))
            self.draw_main_logo(96,30)
            dtext_opt(160, 135, C_WHITE if self.menu_idx == 0 else C_BLACK, 43463, DTEXT_CENTER, DTEXT_MIDDLE, "New Game", -1)
            dtext_opt(160, 165, C_WHITE if self.menu_idx == 1 else C_BLACK, 43463, DTEXT_CENTER, DTEXT_MIDDLE, "Exit", -1)

        elif self.state == 'playing':
            self.draw_map_edited()
            self.map.edited.clear()
            
            for entity in self.entities:
                if (
                    entity.position.x - self.camera.x > -18 and
                    entity.position.x - self.camera.x < DW-14 and
                    entity.position.y - self.camera.y > -18 and
                    entity.position.y - self.camera.y < DH-14
                ):
                    entity.draw()
                else:
                    entity.draw_outside()
            
            # for x, y, image, sx, sy, sw, sh in self.to_draw_calls:
            #     dsubimage(x, y, image, sx, sy, sw, sh)
            
            for args in self.to_draw_calls:
                dsubimage(*args)
            
            if self.debug_mode:
                for entity in self.entities:
                    entity._debug_hitbox()
            self.to_draw_calls.clear()

            if self.refreshLife:
                self.draw_gauge_life(0, 0, self.player.health / 100.0)
            if self.refreshCrystal:
                self.draw_gauge_crystal((DW//2)-31, 0, self.crystal_hp / 100.0)
        
        elif self.state == 'paused':
            self.draw_panel(Vec2(220, 50),Vec2(330, 130))
            dtext_opt(275, 75, C_WHITE if self.pause_idx == 0 else C_BLACK, 43463, DTEXT_CENTER, DTEXT_MIDDLE, "Resume", -1)
            dtext_opt(275, 105, C_WHITE if self.pause_idx == 1 else C_BLACK, 43463, DTEXT_CENTER, DTEXT_MIDDLE, "Exit", -1)
        
        elif self.state == 'gameover':
            # TODO: should be a separate scene ?
            dclear(C_BLACK)
            self.draw_main_logo(96, 30)
            dtext_opt(DW//2, 130, C_WHITE, C_BLACK, DTEXT_CENTER, DTEXT_MIDDLE, "Game Over", -1)
            dtext_opt(DW//2, 170, C_WHITE, C_BLACK, DTEXT_CENTER, DTEXT_MIDDLE, "Press EXE for Menu", -1)
            
    # --- Ported Helper Methods ---
    def spawn_skeleton(self):
        node = random.choice(templewa_data.spawnable_ids)
        self.entities.append(Skeleton(self, node))
    
    def move_camera(self, x: int, y: int):
        self.camera = Vec2(x, y)
        self.draw_map_full()
        self.timer.reset()

    def change_life(self, value: int):
        self.player.health = max(0, value)
    
    def change_crystal(self, value: int):
        self.crystal_hp = max(0, value)

    def draw_subimage(self, x, y, image, sx, sy, sw, sh):
        self.to_draw_calls.append((
            int(x), int(y), image,
            int(round(sx)), int(round(sy)),
            int(round(sw)), int(round(sh))
        ))
        # Mark underlying tiles as dirty
        world_x, world_y = round(x + self.camera.x), round(y + self.camera.y)
        x_start, y_start = (world_x // 16), (world_y // 16) # // 16
        x_end, y_end = (world_x + sw) // 16, (world_y + sh) // 16
        for i in range(x_start, x_end + 1):
            for j in range(y_start, y_end + 1):
                self.map.add_refresh(i, j)

    def draw_map_full(self):
        dclear(C_BLACK) # Or a background color
        for y in range(
            max(0, self.camera.y // self.map.tile_size),
            min(self.map.height, ((self.camera.y + DH) // self.map.tile_size)),
            1
        ): # self.map.height
            for x in range(
                max(0, self.camera.x // self.map.tile_size),
                min(self.map.width, ((self.camera.x + DW) // self.map.tile_size) + 1)
            ): # self.map.width
                self.draw_tile(x, y)
        self.refreshCrystal = True
        self.refreshLife = True
    
    def draw_map_edited(self):
        for x, y in self.map.edited:
            self.draw_tile(x, y)

            draw_y = int((y * self.map.tile_size) - self.camera.y)
            if draw_y <= 16:
                self.refreshCrystal = True
                self.refreshLife = True
    
    def draw_tile(self, x, y):
        tile_id = self.map.get(x, y)
        # if tile_id == 34: return # Assuming 34 is empty space from the original map data
        
        tile_x = (tile_id % 5) * self.map.tile_size
        tile_y = (tile_id // 5) * self.map.tile_size
        draw_x = int((x * self.map.tile_size) - self.camera.x)
        draw_y = int((y * self.map.tile_size) - self.camera.y)
        
        dsubimage(draw_x, draw_y, templewa_data.tiles, tile_x, tile_y, self.map.tile_size, self.map.tile_size)

    def draw_main_logo(self, x, y):
        dsubimage(x, y, templewa_data.ui, 0, 0, 122, 59)
        dsubimage(x + 122, y + 37, templewa_data.ui, 122, 37, 158 - 122, 59 - 37)

    def draw_gauge_life(self, x, y, percent):
        drect(x + 15, y + 7, x + 60, y + 9, C_BLACK)
        ext = int((60 - 15) * percent)
        if ext > 0: drect(x + 15, y + 7, x + 15 + ext, y + 9, C_RED)
        dsubimage(x, y, templewa_data.ui, 0, 60, 64, 15)

    def draw_gauge_crystal(self, x, y, percent):
        drect(x + 3, y + 8, x + (129 - 68 - 3), y + 10, C_BLACK)
        ext = int((129 - 68 - 6) * percent)
        if ext > 0: drect(x + 3, y + 8, x + 3 + ext, y + 10, C_RED)
        dsubimage(x, y, templewa_data.ui, 68, 60, 129 - 68, 15)
        
    def draw_panel(self, tl: Vec2, br: Vec2):
        ui_img = templewa_data.ui
        # TODO: Draw NineSlice
        dsubimage(tl.x, tl.y, ui_img, 124, 0, 17, 17)
        dsubimage(tl.x, br.y-17, ui_img, 124, 19, 17, 17)
        dsubimage(br.x-17, tl.y, ui_img, 124 + 19, 0, 17, 17)
        dsubimage(br.x-17, br.y-17, ui_img, 124 + 19, 19, 17, 17)
        for i in range(tl.x + 17, br.x - 16):
            dsubimage(i, tl.y, ui_img, 124 + 18, 0, 1, 17)
            dsubimage(i, br.y-17, ui_img, 124 + 18, 19, 1, 17)
        for i in range(tl.y + 17, br.y - 16):
            dsubimage(tl.x, i, ui_img, 124, 18, 17, 1)
            dsubimage(br.x-17, i, ui_img, 124 + 19, 18, 17, 1)
        drect(tl.x+17, tl.y+17, br.x-17, br.y-17, 43463)