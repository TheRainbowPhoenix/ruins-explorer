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
from cpgame.engine.logger import log
from cpgame.engine.text_parser import parse_text_codes

TILE_SIZE = 20
MOVE_DELAY = 0.15

class JRPGScene(Scene):
    """
    Implements the top-down exploration gameplay.
    Features grid-based movement, a block-based camera, and a dialog system.
    """
    def __init__(self, game):
        super().__init__(game)

        if not JRPG.objects:
            raise Exception("No JRPG data loaded !")
        
        # --- Game Objects references ---
        self.map = JRPG.objects.map
        self.player = JRPG.objects.player
        
        # --- Game State ---
        self.tileset = None
        self.player.x: int = 0 # TODO: should be in player
        self.player.y: int = 0
        self.move_cooldown: float = 0.0

        # --- Map Data ---
        self.tileset = None
        # self.map_layout: List[List[int]] = []
        # self.map_objects: Dict[Tuple[int, int], Tuple[int, Any]] = {} # Use Any for payload
        # self.map_signs: Dict[Tuple[int, int], List[str]] = {}
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
        self.tileset = self.assets.tilesets.get(self.map.tileset_id)
        # self.tileset = self.assets.tilesets["jrpg"]
        
        # map_asset = self.assets.maps["jrpg_village"]
        # self.map_layout = map_asset["layout"]
        # self.map_objects = map_asset["objects"]
        # self.map_signs = map_asset["signs"]
        self.map_h = self.map.height # len(self.map_layout)
        self.map_w = self.map.width # len(self.map_layout[0])

        # Set player's starting position
        # TODO: should not be done here. player should do it.
        self.player.x = self.map_w // 2
        self.player.y = self.map_h // 2

        # Initialize the camera's first position
        self._update_camera_block()
        self.full_redraw_needed = True

    def update(self, dt: float) -> Optional[str]:
        """
        Main logic update, called every fixed timestep.
        """
        # First, poll the input state for this frame
        self.input.update()

        # --- State Machine ---
        if JRPG.objects:
            if JRPG.objects.timer:
                JRPG.objects.timer.update(dt)
            
            if JRPG.objects.growth_manager:
                JRPG.objects.growth_manager.update(dt)

            if JRPG.objects.dialog_in_progress:
                self._update_dialog()
                return None # Prevent any other game logic from running

        # --- Exploring State Logic ---
        # Handle scene transitions first
        if self.input.exit:
            # We import here to avoid circular dependency issues
            from cpgame.game_scenes.menu_scene import MenuScene
            self.game.clear_session() # Clean up party, datamanager, etc.
            return self.game.change_scene(MenuScene)

        # Update the map, which in turn updates events and its interpreter
        self.map.update()

        dirty_from_map = self.map.get_dirty_tiles()
        if dirty_from_map:
            self.dirty_tiles.update(dirty_from_map)

        # Update timers
        if self.move_cooldown > 0:
            self.move_cooldown -= dt

        
        # Player movement is only possible if the event interpreter is not running
        if not self.map.interpreter.is_running():
            self._handle_player_movement()
            self._handle_player_interaction()

        if self._check_for_map_transfer():
            return None

        return None
    
    def _check_for_map_transfer(self) -> bool:
        """Checks if a map transfer has been requested."""
        if self.player.transfer_pending:
            self.draw_loading_screen()

            # print("Executing map transfer...")
            self.player.perform_transfer()
            # Re-initialize this scene's view of it.
            if JRPG.objects:
                self.map = JRPG.objects.map
                self.player = JRPG.objects.player
                self.create() # Re-run create to sync tileset and camera
                return True
        return False
    
    def draw_loading_screen(self):
        """Clears the screen and draws a centered 'Loading...' message."""
        dclear(C_BLACK)
        text = "Loading..."
        
        try:
            w, h = dsize(text, None) # Use default font
        except:
            w, h = len(text) * 8, 16 # Fallback size
            
        x = (DWIDTH - w) // 2
        y = (DHEIGHT - h) // 2
        dtext(x, y, C_WHITE, text)
        dupdate() # Force the screen to update immediately

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

        # if self.dialog_active:
        if JRPG.objects and JRPG.objects.dialog_in_progress:
            self._draw_dialog_box()

    # --- Private Update Helpers ---

    def _update_dialog(self):
        """Handles input logic when a dialog box is active."""
        if self.input.interact:
            # Instead of managing pages locally, we just tell the system to clear the dialog
            if JRPG.objects:
                JRPG.objects.clear_dialog()
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

        next_x, next_y = self.player.x + dx, self.player.y + dy

        if dx != 0:
            next_x, next_y = self.player.x + dx, self.player.y
            if self.tileset and self.map.is_passable(next_x, next_y, self.tileset):
                self._move_player_to(next_x, next_y)
        elif dy != 0:
            next_x, next_y = self.player.x, self.player.y + dy
            if self.tileset and self.map.is_passable(next_x, next_y, self.tileset):
                self._move_player_to(next_x, next_y)
    
    def _move_player_to(self, next_x, next_y):
        """Updates player state and marks tiles for redraw."""
        old_pos = (self.player.x, self.player.y)
        self.player.moveto(next_x, next_y)

        self.move_cooldown = MOVE_DELAY
        
        # Mark tiles for redraw
        self.dirty_tiles.add(old_pos)
        self.dirty_tiles.add((self.player.x, self.player.y))
        
        # Check if the camera needs to move to a new screen block
        if self._update_camera_block():
            self.full_redraw_needed = True

    def _handle_player_interaction(self):
        """Checks for interaction with objects or signs."""
        if not self.input.interact:
            return
        
        #C heck for passable events on the player's current tile
        event_here = self.map.events.get((self.player.x, self.player.y))
        if event_here and event_here.through:
            event_here.start()
            return

        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            adj_pos = (self.player.x + dx, self.player.y + dy)
            event_there = self.map.events.get(adj_pos)
            if event_there and not event_there.through:
                event_there.start()
                return
    
    def _update_camera_block(self) -> bool:
        """
        Updates the camera to a new screen-sized "block" if the player has moved into one.
        Returns True if the camera moved, False otherwise.
        """
        new_block_x = self.player.x // self.screen_tiles_x
        new_block_y = self.player.y // self.screen_tiles_y

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
                # TODO: clamp instead of if each loop ? 
                if 0 <= map_y < self.map_h and 0 <= map_x < self.map_w:
                    self._draw_tile_at(map_x, map_y)

    def _draw_tile_at(self, map_x: int, map_y: int):
        """Redraws a single tile on the map, including any object on it."""
        screen_x, screen_y = self._world_to_screen(map_x, map_y)
        
        # Culling: Don't draw if it's off-screen
        if not (-TILE_SIZE < screen_x < DWIDTH and -TILE_SIZE < screen_y < DHEIGHT):
            return

        # Draw base map tile
        tile_id = self.map.tile_id(map_x, map_y)
        src_x = (tile_id % 16) * TILE_SIZE
        src_y = (tile_id // 16) * TILE_SIZE
        dsubimage(screen_x, screen_y, self.tileset.img, src_x, src_y, TILE_SIZE, TILE_SIZE) # type: ignore

        # Draw object on top, if any
        event = self.map.events.get((map_x, map_y))
        if event and event.tile_id > 0:
            obj_id = event.tile_id
            obj_src_x = (obj_id % 16) * TILE_SIZE
            obj_src_y = (obj_id // 16) * TILE_SIZE
            dsubimage(screen_x, screen_y, self.tileset.img, obj_src_x, obj_src_y, TILE_SIZE, TILE_SIZE) # type: ignore

    def _draw_player(self):
        """Draws the player representation on the screen."""
        scr_x, scr_y = self._world_to_screen(self.player.x, self.player.y)
        center_x = scr_x + TILE_SIZE // 2
        center_y = scr_y + TILE_SIZE // 2
        dcircle(center_x, center_y, TILE_SIZE // 2 - 2, C_BLUE, C_NONE)

    def _draw_dialog_box(self):
        """Draws the UI for the dialog box at the bottom of the screen."""
        box_h = DHEIGHT // 3
        y0 = DHEIGHT - box_h
        drect(0, y0, DWIDTH - 1, DHEIGHT - 1, C_WHITE)
        drect_border(0, y0, DWIDTH - 1, DHEIGHT - 1, C_NONE, 1, C_BLACK)

        if JRPG.objects and JRPG.objects.dialog_pages:
            pages = JRPG.objects.dialog_pages
            for i, line in enumerate(pages):
                final_text = parse_text_codes(line)
                dtext(8, y0 + 8 + i * 16, C_BLACK, final_text)
    
