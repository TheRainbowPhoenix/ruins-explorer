# cpgame/game_scenes/scene_map.py
import gc
import sys
import time
from gint import *
try:
    from typing import Optional, List, Set, Tuple,Dict, Any
except:
    pass

from cpgame.systems.jrpg import JRPG
# from cpgame.engine.scene import Scene
from cpgame.engine.systems import Camera
# from cpgame.game_objects.actor import GameActor
from cpgame.game_scenes._scenes_base import SceneBase

# from cpgame.game_windows.window_base import WindowBase
# from cpgame.game_windows.window_selectable import WindowSelectable
from cpgame.game_windows.window_hud import WindowHUD
from cpgame.game_windows.window_message import WindowMessage
from cpgame.game_windows.window_number_input import WindowNumberInput
# from cpgame.game_windows.window_name_edit import WindowNameEdit
# from cpgame.game_windows.window_name_input import WindowNameInput
# from cpgame.game_windows.window_choice_list import WindowChoiceList


from cpgame.engine.logger import log
from cpgame.engine.text_parser import parse_text_codes

TILE_SIZE = 8
MOVE_DELAY = 0.15


class WindowProxy:
    """Context manager for on-demand window loading and cleanup."""
    def __init__(self, module_path, class_name, *args, **kwargs):
        self.module_path = module_path
        self.class_name = class_name
        self.args = args
        self.kwargs = kwargs
        self.instance = None
        self.module = None

    def __enter__(self):
        # Import module dynamically
        try:
            self.module = __import__(self.module_path, None, None, (self.class_name,))
            window_class = getattr(self.module, self.class_name)
            # Create instance with both args and kwargs
            self.instance = window_class(*self.args, **self.kwargs)
            return self.instance
        except Exception as e:
            log(f"WindowProxy error: {e}")
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.instance:
            if hasattr(self.instance, 'destroy'):
                self.instance.destroy()
            del self.instance

        if self.module:
            # Clean up module attributes
            module_name = self.module_path
            if hasattr(self.module, '__dict__'):
                attrs = list(self.module.__dict__.keys())
                for attr in attrs:
                    if not attr.startswith('__'):
                        try:
                            delattr(self.module, attr)
                        except:
                            pass

            # Remove from sys.modules
            if module_name in sys.modules:
                try:
                    sys.modules.pop(module_name)
                except:
                    pass

            del self.module

        gc.collect()

class OptimizedTileCache:
    """Optimized tile rendering with batching."""
    __slots__ = ('_batch_data', '_batch_count', '_last_tileset')

    def __init__(self):
        self._batch_data = bytearray(256)  # Pre-allocated buffer
        self._batch_count = 0
        self._last_tileset = None

    def add_tile(self, screen_x, screen_y, tile_id):
        """Add tile to batch render queue."""
        if self._batch_count < 64:  # Max batch size
            idx = self._batch_count * 4
            self._batch_data[idx] = screen_x & 0xFF
            self._batch_data[idx + 1] = screen_y & 0xFF
            self._batch_data[idx + 2] = tile_id & 0xFF
            self._batch_data[idx + 3] = (tile_id >> 8) & 0xFF
            self._batch_count += 1
            return True
        return False

    def flush(self, tileset):
        """Render all batched tiles."""
        if not self._batch_count or not tileset:
            return

        for i in range(self._batch_count):
            idx = i * 4
            screen_x = self._batch_data[idx]
            screen_y = self._batch_data[idx + 1]
            tile_id = self._batch_data[idx + 2] | (self._batch_data[idx + 3] << 8)

            src_x = (tile_id & 15) << 5  # (tile_id % 16) * TILE_SIZE, optimized
            src_y = (tile_id >> 4) << 5  # (tile_id // 16) * TILE_SIZE, optimized
            dsubimage(screen_x, screen_y, tileset.img, src_x, src_y, TILE_SIZE, TILE_SIZE)

        self._batch_count = 0

class SceneMap(SceneBase):
    """This class performs the map screen processing."""
    def __init__(self, game, **kwargs):
        super().__init__(game, **kwargs)
        if not JRPG.objects:
            raise Exception("SceneMap requires JRPG session data.")
        
        self.map = JRPG.objects.map
        self.player = JRPG.objects.player
        self.tileset = None
        self.move_cooldown = 0.0
        
        # Rendering
        self.camera = Camera()
        self.hud_window = WindowHUD()
        # self.message_window = WindowMessage()
        self._map_render_offset_y = self.hud_window.height
        self.cam_block_x, self.cam_block_y = -1, -1
        self.screen_tiles_x = DWIDTH // TILE_SIZE
        self.screen_tiles_y = (DHEIGHT - self._map_render_offset_y) // TILE_SIZE
        
        # --- Rendering Optimization ---
        self.dirty_tiles: Set[Tuple[int, int]] = set()
        self.full_redraw_needed = True
    

    def create(self):
        log("SceneMap: Creating...")
        # Load assets required for this scene
        self.tileset = self.assets.get_tileset(self.map.tileset_id) # 'jrpg'
        if not self.tileset:
            raise Exception(f"Failed to load '{self.map.tileset_id}' tileset.")

        # Create the windows managed by this scene
        self.message_window = WindowMessage()
        self.hud_window._needs_redraw = True
        self.number_input_window = WindowNumberInput(
            on_confirm=self.on_number_input_confirm,
            on_cancel=self.on_number_input_cancel
        )
        # self.name_edit_window = WindowNameEdit(JRPG.objects.actors[1] if JRPG.objects else None, 8) # Placeholder
        # self.name_input_window = WindowNameInput(self.name_edit_window)
        # self.name_input_window.set_handler('ok', self.on_name_input_confirm)
        # self.name_input_window.set_handler('cancel', self.on_name_input_cancel)

        # self.choice_window = WindowChoiceList(self.message_window)
        # self.choice_window.set_handler('ok', self.on_choice_confirm)
        # self.choice_window.set_handler('cancel', self.on_choice_cancel)

        self._windows = [
            self.hud_window,
            self.message_window,
            self.number_input_window,
            # self.name_edit_window, self.name_input_window,
            # self.choice_window
        ]
        
        self._update_camera_block()
        self.full_redraw_needed = True

    def resume(self):
        """Called when returning from a child scene (like a menu or shop)."""
        log("SceneMap: Resuming...")
        self.full_redraw_needed = True

    def destroy(self):
        """Called when this scene is being replaced. Unloads assets."""
        log("SceneMap: Destroying...")
        self.assets.unload(self.map.tileset_id) # self.map.tileset_id  # 'jrpg'
        for w in self._windows: w.destroy()
        self._windows.clear()
        self.dirty_tiles.clear()
        gc.collect()

    def update(self, dt: float):
        # First, poll the input state for this frame
        # self.input.update()
        
        # --- State Machine ---
        if JRPG.objects:
            if JRPG.objects.timer:
                JRPG.objects.timer.update(dt)
            
            if JRPG.objects.growth_manager:
                JRPG.objects.growth_manager.update(dt)

            # if JRPG.objects.dialog_in_progress:
            #     self._update_dialog()
            #     return None # Prevent any other game logic from running
        
        # Update the map, which in turn updates events and its interpreter
        self.map.update()

        # Update all windows
        for window in self._windows:
            window.update()
        
        if self._active_window:
            # If a modal window is active, it gets all input
            self._active_window.handle_input(self.input) # update ? handle_input ?
            # Add touch handling placeholder
            # touch = get_touch_event() 
            # if touch: self._active_window.handle_touch(touch.x, touch.y)

            return None


        # super().update(dt)
        # if self._active_window: return # Pause map logic if a modal window is active

        
        if JRPG.objects and JRPG.objects.message:
            if JRPG.objects.message.is_number_input():
                self.start_number_input()
                return None
            if JRPG.objects.message.is_name_input():
                self._handle_name_input()
                return None
            if JRPG.objects.message.is_choice():
                self._handle_choice_input()
                return None

        
        if JRPG.objects and JRPG.objects.message and JRPG.objects.message.is_busy():
            # self.message_window.on_confirm(self.input)
            self._update_dialog()
            return None # Pause game logic while message is showing

        # Update dirty tiles from map
        dirty_from_map = self.map.get_dirty_tiles()
        if dirty_from_map:
            self.dirty_tiles.update(dirty_from_map)

        # Update timers
        if self.move_cooldown > 0:
            self.move_cooldown -= dt

        # Normal map logic
        if not self.map.interpreter.is_running():
            # if self.move_cooldown > 0: self.move_cooldown -= dt
            self._handle_player_movement()
            self._handle_player_interaction()
        
        self.update_scene_change_check()

    def update_scene_change_check(self):
        """Handles transitions to other scenes."""
        if self.player.transfer_pending:
            self.perform_transfer()
        # Add calls to menu, battle, etc. here
        elif self.input.exit:
            from .menu_scene import MenuScene # Local import
            self.game.call_scene(MenuScene)

    def perform_transfer(self):
        """Executes a map transfer by changing to a new SceneMap."""
        log("Performing map transfer...")
        self.draw_loading_screen()
        # Preserve the player's new position state
        self.player.perform_transfer()
        # Re-initialize this scene's view of it.
        if JRPG.objects:
            self.map = JRPG.objects.map
            self.player = JRPG.objects.player
            self.create() # Re-run create to sync tileset and camera
            return True
        
        self.hud_window._needs_redraw = True
        # Replace the current SceneMap with a new one
        # self.game.change_scene(SceneMap)
        return False

    def draw(self, frame_time_ms: int):
        if self.full_redraw_needed:
            self._draw_viewport()
            self.full_redraw_needed = False
        elif self.dirty_tiles:
            for tx, ty in self.dirty_tiles:
                self._draw_tile_at(int(tx), int(ty))
        self.dirty_tiles.clear()

        self._draw_player()

        super().draw(frame_time_ms) # Draws all windows

    # --- Private Update Helpers ---

    def _update_dialog(self):
        """
        Handles input logic when a dialog box is active. This is the only
        place that should process input during a dialog.
        """
        # Tell the message window that a confirmation was pressed.
        # The window itself will handle the consequences.
        if self.input.interact:
            self.message_window.on_confirm(self.input)
            # After closing, the map might have changed (e.g., event page switched)
            self.full_redraw_needed = True 
            self.hud_window._needs_redraw = True
    
    def start_number_input(self):
        """Activates the number input window."""
        if not JRPG.objects:
            return 
        
        msg = JRPG.objects.message
        var_id = msg.number_input_variable_id
        if var_id is not None:
            initial_value = JRPG.objects.variables.value(var_id)
        
            self.number_input_window.start(initial_value, msg.number_input_digits_max)
            self._active_window = self.number_input_window
    
    def on_number_input_confirm(self, number: int):
        """Callback for when the user confirms a number."""
        if not JRPG.objects:
            return
        
        msg = JRPG.objects.message
        var_id = msg.number_input_variable_id
        if var_id:
            JRPG.objects.variables.set(var_id, number)
            log("Update V[{}] to {}".format(var_id, number))
        
            self.number_input_window.active = False
            self.number_input_window.visible = False
            self._active_window = None
            JRPG.objects.message.clear() # Clear the request
            JRPG.objects.message._number_input_variable_id = None
            self.full_redraw_needed = True
            self.hud_window._needs_redraw = True
    
    def _handle_name_input(self):
        if not JRPG.objects:
            return
        
        msg = JRPG.objects.message
        if not msg.name_input_actor_id:
            return

        actor = JRPG.objects.actors[msg.name_input_actor_id]
        if not actor:
            msg.clear()
            return

        # Unload tileset temporarily to save memory
        self.assets.unload(self.map.tileset_id) # 'jrpg'
        
        # Use keyword arguments for proper instantiation
        with WindowProxy('cpgame.game_windows.window_name_edit', 'WindowNameEdit') as name_edit_window:
            with WindowProxy('cpgame.game_windows.window_name_input', 'WindowNameInput') as name_input_window:

                name_input_window.set_handler('ok', lambda name: self._on_name_confirmed(actor, name))
                name_input_window.set_handler('cancel', self._on_name_cancelled)

                # name_edit_window.visible = True
                # name_input_window.visible = True
                # name_input_window.activate()
                name_input_window.start(name_edit_window)
                name_edit_window.start(actor, msg.name_input_max_chars)
                self._active_window = name_input_window

                # Handle input loop within context
                while self._active_window == name_input_window:
                    frame_start_time = time.ticks_ms()

                    self.input.update()

                    name_input_window.handle_input(self.input)
                    name_input_window.update()
                    name_edit_window.update()
                    # render_start_time = time.ticks_ms()

                    name_input_window.draw() # time.ticks_diff(time.ticks_ms(), render_start_time))
                    name_edit_window.draw()
                    dupdate()

                    frame_time_ms = time.ticks_diff(time.ticks_ms(), frame_start_time)
                    # if DEBUG_FRAME_TIME: print(f"Frame Time: {frame_time_ms}ms")
                    if frame_time_ms < self.game.frame_cap_ms:
                        time.sleep_ms(self.game.frame_cap_ms - frame_time_ms)


        # Reload tileset
        self.tileset = self.assets.get_tileset(self.map.tileset_id) # 'jrpg'
        self.full_redraw_needed = True
        self.hud_window._needs_redraw = True

    def _handle_choice_input(self):
        """Handle choice input using WindowProxy."""
        if not JRPG.objects:
            return
        
        msg = JRPG.objects.message

        # Temporarily unload tileset
        self.assets.unload(self.map.tileset_id) # 'jrpg'

        with WindowProxy('cpgame.game_windows.window_choice_list', 'WindowChoiceList', self._windows[1]) as choice_window:  # message_window
            choice_window.set_handler('ok', self._on_choice_confirmed)
            choice_window.set_handler('cancel', self._on_choice_cancelled)
            choice_window.start(msg.choices, msg.choice_cancel_type, self._on_choice_made)
            self._active_window = choice_window

            # Handle input loop within context
            while self._active_window == choice_window:
                frame_start_time = time.ticks_ms()

                self.input.update()

                choice_window.handle_input(self.input)
                choice_window.update()
                # render_start_time = time.ticks_ms()

                choice_window.draw() # time.ticks_diff(time.ticks_ms(), render_start_time))
                dupdate()

                frame_time_ms = time.ticks_diff(time.ticks_ms(), frame_start_time)
                # if DEBUG_FRAME_TIME: print(f"Frame Time: {frame_time_ms}ms")
                if frame_time_ms < self.game.frame_cap_ms:
                    time.sleep_ms(self.game.frame_cap_ms - frame_time_ms)

        # Reload tileset
        self.tileset = self.assets.get_tileset(self.map.tileset_id) # 'jrpg'
        self.full_redraw_needed = True
        self.hud_window._needs_redraw = True

    def _on_name_confirmed(self, actor, name):
        actor.name = name
        self._active_window = None
        if JRPG.objects:
            JRPG.objects.message.clear()

    def _on_name_cancelled(self):
        self._active_window = None
        if JRPG.objects:
            JRPG.objects.message.clear()

    def _on_choice_confirmed(self, index):
        if JRPG.objects and JRPG.objects.message.choice_variable_id is not None:
            JRPG.objects.variables[JRPG.objects.message.choice_variable_id] = index + 1
        self._end_modal_input()

    def _on_choice_cancelled(self):
        if JRPG.objects and JRPG.objects.message.choice_variable_id is not None:
            JRPG.objects.variables[JRPG.objects.message.choice_variable_id] = 0
        self._end_modal_input()

    def _on_choice_made(self, index):
        if JRPG.objects and JRPG.objects.message.choice_callback:
            JRPG.objects.message.choice_callback(index)
        self._end_modal_input()

    def _end_modal_input(self):
        self._active_window = None
        if JRPG.objects:
            JRPG.objects.message.clear()
        self.full_redraw_needed = True
        self.hud_window._needs_redraw = True


    def on_choice_made(self, index: int):
        if JRPG.objects: 
            msg = JRPG.objects.message
            if msg.choice_callback:
                msg.choice_callback(index)
        
        self._end_modal_input(self.choice_window)

    def on_name_input_confirm(self, name: str):
        if not JRPG.objects:
            return
        
        msg = JRPG.objects.message
        var_id = msg.number_input_variable_id
        if var_id:
            JRPG.objects.variables.set(var_id, number)
            log("Update V[{}] to {}".format(var_id, number))
        
        actor = JRPG.objects.actors[msg.name_input_actor_id]
        if actor: actor.name = name

        self.name_edit_window.visible = False
        self.name_input_window.visible = False
        self.name_input_window.deactivate()

        if self.name_edit_window in self._windows:
            self._windows.remove(self.name_edit_window)
        if self.name_input_window in self._windows:
            self._windows.remove(self.name_input_window)
        
        del self.name_edit_window 
        del self.name_input_window

        self.name_edit_window = None
        self.name_input_window = None

        self._active_window = None
        msg.clear()
        self.full_redraw_needed = True
        self.hud_window._needs_redraw = True
        # cleanup
        gc.collect()

    def on_number_input_cancel(self):
        """Callback for when the user cancels number input."""
        self.number_input_window.active = False
        self.number_input_window.visible = False
        self._active_window = None
        if JRPG.objects:
            JRPG.objects.message.clear()
        self.full_redraw_needed = True
        self.hud_window._needs_redraw = True

    def on_choice_confirm(self, index: int):
        if not JRPG.objects:
            return
        msg = JRPG.objects.message
        # Store the 1-based index in the designated variable
        if msg.choice_variable_id is not None:
            JRPG.objects.variables[msg.choice_variable_id] = index + 1
        self._end_modal_input(self.choice_window)

    def on_choice_cancel(self):
        if not JRPG.objects:
            return
        
        msg = JRPG.objects.message
        # Store the cancel value (0)
        if msg.choice_variable_id is not None:
            JRPG.objects.variables[msg.choice_variable_id] = 0
        self._end_modal_input(self.choice_window)

    def on_name_input_cancel(self):
        """Callback for when the user cancels number input."""
        self.name_edit_window.visible = False
        self.name_input_window.visible = False
        self.name_input_window.deactivate()

        if self.name_edit_window in self._windows:
            self._windows.remove(self.name_edit_window)
        if self.name_input_window in self._windows:
            self._windows.remove(self.name_input_window)
        
        del self.name_edit_window 
        del self.name_input_window
        
        self.name_edit_window = None
        self.name_input_window = None
        
        self._active_window = None
        if JRPG.objects:
            JRPG.objects.message.clear()
        self.full_redraw_needed = True
        self.hud_window._needs_redraw = True
    
    # def _end_modal_input(self, window):
    #     """Generic helper to close any modal window.""" 
    #     window.visible = False
    #     window.deactivate()
    #     self._active_window = None
    #     if JRPG.objects:
    #         JRPG.objects.message.clear()
    #     self.full_redraw_needed = True
    
    # --- Move helper ---

    def _handle_player_movement(self):
        """Checks for and processes player movement input."""
        if self.move_cooldown > 0:
            return

        dx = dy = 0
        if self.input.dx > 0:
            dx = 1
        elif self.input.dx < 0:
            dx = -1
        elif self.input.dy > 0:
            dy = 1
        elif self.input.dy < 0:
            dy = -1
        
        if dx == 0 and dy == 0:
            return

        next_x = self.player.x + dx
        next_y = self.player.y + dy

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
            self.hud_window._needs_redraw = True

    def _handle_player_interaction(self):
        """Checks for interaction with objects or signs."""
        if not self.input.interact:
            return
        
        #C heck for passable events on the player's current tile
        event_here = self.map.events.get((self.player.x, self.player.y))
        if event_here and event_here.through:
            event_here.start()
            return

        # Check adjacent tiles
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
        # return (world_x * TILE_SIZE - self.camera.x, world_y * TILE_SIZE - self.camera.y)
        screen_x = world_x * TILE_SIZE - self.camera.x
        screen_y = world_y * TILE_SIZE - self.camera.y + self._map_render_offset_y
        return (screen_x, screen_y)

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
                if 0 <= map_y < self.map.height and 0 <= map_x < self.map.width:
                    self._draw_tile_at(map_x, map_y)

    def _draw_tile_at(self, map_x: int, map_y: int):
        """Redraws a single tile on the map, including any object on it."""
        screen_x, screen_y = self._world_to_screen(map_x, map_y)

        top_bound = self._map_render_offset_y - TILE_SIZE
        bottom_bound = DHEIGHT
        
        # Culling: Don't draw if it's off-screen
        if not (-TILE_SIZE < screen_x < DWIDTH and top_bound < screen_y < bottom_bound):
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
