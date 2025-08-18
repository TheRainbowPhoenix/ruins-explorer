# scenes/jrpg_scene.py
from gint import *
try:
    from typing import Optional, List, Set, Tuple,Dict, Any
except:
    pass

from cpgame.systems.jrpg import JRPG
from cpgame.engine.scene import Scene
from cpgame.engine.systems import Camera
from cpgame.game_objects.actor import GameActor

TILE_SIZE = 20
MOVE_DELAY = 0.15

class JRPGScene(Scene):
    """
    Implements the top-down exploration gameplay.
    Features grid-based movement, a block-based camera, and a dialog system.
    """
    def __init__(self, game):
        super().__init__(game)
        
        # --- Game State ---
        self.player_x: int = 0
        self.player_y: int = 0
        self.move_cooldown: float = 0.0

        # --- Map Data ---
        self.tileset = None
        self.map_layout: List[List[int]] = []
        self.map_objects: Dict[Tuple[int, int], Tuple[int, Any]] = {} # Use Any for payload
        self.map_signs: Dict[Tuple[int, int], List[str]] = {}
        self.map_w: int = 0
        self.map_h: int = 0

        # --- Camera & Rendering ---
        self.cam_block_x: int = -1
        self.cam_block_y: int = -1
        self.screen_tiles_x = DWIDTH // TILE_SIZE
        self.screen_tiles_y = DHEIGHT // TILE_SIZE
        
        # --- Rendering Optimization ---
        self.dirty_tiles: Set[Tuple[int, int]] = set()
        self.full_redraw_needed = True

        # --- Dialog State ---
        self.dialog_active: bool = False
        self.dialog_pages: List[str] = []
        self.dialog_index: int = 0

    
        
    def create(self):
        """
        Called once by the game loop when this scene starts.
        Responsible for loading assets and setting up initial state.
        """
        # print("JRPGScene: Creating...")

        # Load all necessary assets from the manager
        self.tileset = self.assets.tilesets["jrpg"]
        map_asset = self.assets.maps["jrpg_village"]
        self.map_layout = map_asset["layout"]
        self.map_objects = map_asset["objects"]
        self.map_signs = map_asset["signs"]
        self.map_h = len(self.map_layout)
        self.map_w = len(self.map_layout[0])

        # Set player's starting position
        self.player_x = self.map_w // 2
        self.player_y = self.map_h // 2

        # Initialize the camera's first position
        self._update_camera_block()
        self.full_redraw_needed = True

    def update(self, dt: float) -> Optional[str]:
        """
        Main logic update, called every fixed timestep.
        """
        # First, poll the input state for this frame
        self.input.update()

        # --- State Machine: Are we in a dialog or exploring? ---
        if self.dialog_active:
            self._update_dialog()
            return None # Prevent any other game logic from running

        # --- Exploring State Logic ---
        # Handle scene transitions first
        if self.input.exit:
            # We import here to avoid circular dependency issues
            from cpgame.game_scenes.menu_scene import MenuScene
            self.game.clear_session() # Clean up party, datamanager, etc.
            return self.game.change_scene(MenuScene)

        # Update timers
        if self.move_cooldown > 0:
            self.move_cooldown -= dt

        # Handle player input for movement and interaction
        self._handle_player_movement()
        self._handle_player_interaction()

        return None

    def draw(self, frame_time_ms: int):
        """
        Main drawing function, called every render frame.
        """
        if self.full_redraw_needed:
            self._draw_viewport()
            self.full_redraw_needed = False
        elif self.dirty_tiles:
            for tx, ty in self.dirty_tiles:
                self._draw_tile_at(tx, ty)

        self.dirty_tiles.clear()

        self._draw_player()

        if self.dialog_active:
            self._draw_dialog_box()

    # --- Private Update Helpers ---

    def _update_dialog(self):
        """Handles input logic when a dialog box is active."""
        if self.input.interact:
            self.dialog_index += 1
            if self.dialog_index >= len(self.dialog_pages):
                # Dialog has ended
                self.dialog_active = False
                self.full_redraw_needed = True # Redraw the world underneath

    def _handle_player_movement(self):
        """Checks for and processes player movement input."""
        if self.move_cooldown > 0:
            return

        # Use dx/dy for direction, but only move one direction at a time
        dx, dy = 0, 0
        if self.input.dx > 0: dx = 1
        elif self.input.dx < 0: dx = -1
        elif self.input.dy > 0: dy = 1
        elif self.input.dy < 0: dy = -1
        
        if dx == 0 and dy == 0:
            return

        next_x, next_y = self.player_x + dx, self.player_y + dy

        if self._is_walkable(next_x, next_y):
            old_pos = (self.player_x, self.player_y)
            self.player_x, self.player_y = next_x, next_y
            
            self.move_cooldown = MOVE_DELAY # Reset timer
            
            # Mark tiles for redraw
            self.dirty_tiles.add(old_pos)
            self.dirty_tiles.add((self.player_x, self.player_y))
            
            # Check if the camera needs to move to a new screen block
            if self._update_camera_block():
                self.full_redraw_needed = True

    def _handle_player_interaction(self):
        """Checks for interaction with objects or signs."""
        if not self.input.interact:
            return

        # Check interaction target in front of the player
        front_x = self.player_x + (1 if self.input.dx > 0 else -1 if self.input.dx < 0 else 0)
        front_y = self.player_y + (1 if self.input.dy > 0 else -1 if self.input.dy < 0 else 0)
        
        # Check adjacent tiles if not moving
        if self.input.dx == 0 and self.input.dy == 0:
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                adj_pos = (self.player_y + dy, self.player_x + dx)
                if self._check_interaction_at(adj_pos):
                    return
        else:
             adj_pos = (self.player_y + self.input.dy, self.player_x + self.input.dx)
             if self._check_interaction_at(adj_pos):
                return
        
        # Fallback to check player's current tile (e.g. for floor items)
        player_pos = (self.player_y, self.player_x)
        if self._check_interaction_at(player_pos):
            return
    
    def _check_interaction_at(self, pos: Tuple[int, int]) -> bool:
        """Helper to check for and handle interaction at a specific map coordinate."""
        if pos in self.map_objects:
            _, payload = self.map_objects[pos]
            # Handle different payload types
            if isinstance(payload, dict) and payload.get("type") == "actor":
                # It's an actor, load it using the DataManager
                actor_id = payload.get("id", None)
                if actor_id and JRPG.objects:
                    # This will lazy-load the actor on first access.
                    actor = JRPG.objects.actors[actor_id]
                    # Could also do self.game.session_data.get('objects') for direct access
                    if actor:
                        actor.hp -= 1 # Modify its state
                        party_info = ["Party Leader: " + str(JRPG.objects.party.leader().name)]
                        self._start_dialog(actor.get_info_text() + party_info)
                    return True
            else:
                # It's a simple dialog object
                self._start_dialog(payload)
                return True # Interaction handled

        # Check for signs
        if pos in self.map_signs:
            pages = self.map_signs[pos]
            self._start_dialog(pages)
            return True # Interaction handled
            
        return False # No interaction found

    def _is_walkable(self, x: int, y: int) -> bool:
        """Checks if a given map coordinate is within bounds and not a solid tile."""
        if not (0 <= y < self.map_h and 0 <= x < self.map_w):
            return False
        
        # Prevent walking on tiles occupied by objects/actors
        tile_id = self.map_layout[y][x]
        # Also consider tiles with objects on them as not walkable
        # TODO: Some should be passable, should be done without needing to query each elements data !!
        if (y, x) in self.map_objects:
            o = self.map_objects.get((x, y))
            if type(o) == object and o.get("type") in ["actor"]:
                return False
        
        return tile_id not in self.tileset.solid # type: ignore

    def _update_camera_block(self) -> bool:
        """
        Updates the camera to a new screen-sized "block" if the player has moved into one.
        Returns True if the camera moved, False otherwise.
        """
        new_block_x = self.player_x // self.screen_tiles_x
        new_block_y = self.player_y // self.screen_tiles_y

        if new_block_x != self.cam_block_x or new_block_y != self.cam_block_y:
            self.cam_block_x = new_block_x
            self.cam_block_y = new_block_y
            self.camera.x = self.cam_block_x * self.screen_tiles_x * TILE_SIZE
            self.camera.y = self.cam_block_y * self.screen_tiles_y * TILE_SIZE
            return True
        return False

    def _start_dialog(self, pages: Any): # List[str]
        """Initializes the dialog system."""
        self.dialog_active = True
        self.dialog_pages = pages
        self.dialog_index = 0

    # --- Private Drawing Helpers ---

    def _world_to_screen(self, world_x: int, world_y: int) -> Tuple[int, int]:
        """Converts world tile coordinates to screen pixel coordinates."""
        return (world_x * TILE_SIZE - self.camera.x, world_y * TILE_SIZE - self.camera.y)

    def _draw_viewport(self):
        """Performs a full redraw of all visible tiles on the screen."""
        dclear(C_BLACK)
        base_x = self.cam_block_x * self.screen_tiles_x
        base_y = self.cam_block_y * self.screen_tiles_y

        # Iterate one tile beyond the screen edge to avoid pop-in
        for ry in range(self.screen_tiles_y + 1):
            for rx in range(self.screen_tiles_x + 1):
                map_x, map_y = base_x + rx, base_y + ry
                if 0 <= map_y < self.map_h and 0 <= map_x < self.map_w:
                    self._draw_tile_at(map_x, map_y)

    def _draw_tile_at(self, map_x: int, map_y: int):
        """Redraws a single tile on the map, including any object on it."""
        screen_x, screen_y = self._world_to_screen(map_x, map_y)
        
        # Culling: Don't draw if it's off-screen
        if not (-TILE_SIZE < screen_x < DWIDTH and -TILE_SIZE < screen_y < DHEIGHT):
            return

        # Draw base map tile
        tile_id = self.map_layout[map_y][map_x]
        src_x = (tile_id % 16) * TILE_SIZE
        src_y = (tile_id // 16) * TILE_SIZE
        dsubimage(screen_x, screen_y, self.tileset.img, src_x, src_y, TILE_SIZE, TILE_SIZE) # type: ignore

        # Draw object on top, if any
        pos = (map_y, map_x)
        if pos in self.map_objects:
            obj_id, _ = self.map_objects[pos]
            obj_src_x = (obj_id % 16) * TILE_SIZE
            obj_src_y = (obj_id // 16) * TILE_SIZE
            dsubimage(screen_x, screen_y, self.tileset.img, obj_src_x, obj_src_y, TILE_SIZE, TILE_SIZE) # type: ignore

    def _draw_player(self):
        """Draws the player representation on the screen."""
        scr_x, scr_y = self._world_to_screen(self.player_x, self.player_y)
        center_x = scr_x + TILE_SIZE // 2
        center_y = scr_y + TILE_SIZE // 2
        dcircle(center_x, center_y, TILE_SIZE // 2 - 2, C_BLUE, C_NONE)

    def _draw_dialog_box(self):
        """Draws the UI for the dialog box at the bottom of the screen."""
        box_h = DHEIGHT // 3
        y0 = DHEIGHT - box_h
        drect(0, y0, DWIDTH - 1, DHEIGHT - 1, C_WHITE)
        drect_border(0, y0, DWIDTH - 1, DHEIGHT - 1, C_NONE, 1, C_BLACK)

        if self.dialog_index < len(self.dialog_pages):
            page_text = self.dialog_pages[self.dialog_index]
            # Handle both list of strings and single string with newlines
            lines_to_draw = page_text if isinstance(page_text, list) else page_text.split("\n")
            for i, line in enumerate(lines_to_draw):
                dtext(8, y0 + 8 + i * 16, C_BLACK, line)
