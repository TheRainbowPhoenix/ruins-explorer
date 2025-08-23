# engine/game.py
# The main game class with the fixed-timestep loop and scene management.

import time
import gc # Import garbage collector for cleanup
from gint import dupdate, dclear, dtext, C_BLACK, DWIDTH, DHEIGHT, C_WHITE
from cpgame.engine.scene import Scene
from cpgame.engine.assets import AssetManager
from cpgame.engine.systems import InputManager
from cpgame.engine.profiler import MemoryProfiler

try:
    from typing import Optional, List, Dict, Any
except:
    pass

DEBUG_FRAME_TIME = False

class Game:
    """The main Game class"""
    def __init__(self):
        self.scenes: List[Scene] = []
        self.assets = AssetManager()
        self.input = InputManager()
        self.running: bool = False
        self.fixed_timestep: float = 0.055
        self.frame_cap_ms: int = 53

        # Generic container for game-mode-specific systems.
        # self.session_data: Dict[str, Any] = {}

    def start(self, initial_scene_class):
        """Initializes assets and starts the game with the first scene."""
        # self.assets.load_all()
        self.running = True
        self.change_scene(initial_scene_class) # Ideally you'd push scenes, but we'd run out of memory
        # self.push_scene(initial_scene_class)

        while self.running and self.scenes:
            frame_start_time = time.ticks_ms()
            current_scene = self.scenes[-1]
            
            self.input.update() # Poll input once per frame
            signal = current_scene.update(self.fixed_timestep)
            if signal == "EXIT_GAME": self.running = False; break

            # --- RENDER ---
            render_start_time = time.ticks_ms()
            current_scene.draw(time.ticks_diff(time.ticks_ms(), render_start_time))
            dupdate()

            # --- FRAME CAP ---
            frame_time_ms = time.ticks_diff(time.ticks_ms(), frame_start_time)
            if DEBUG_FRAME_TIME: print(f"Frame Time: {frame_time_ms}ms")
            if frame_time_ms < self.frame_cap_ms:
                time.sleep_ms(self.frame_cap_ms - frame_time_ms)

    def _draw_loading_screen(self):
        dclear(C_BLACK)
        text = "Loading..."
        w, h = len(text) * 8, 16 # Simple size calculation
        dtext((DWIDTH - w) // 2, (DHEIGHT - h) // 2, C_WHITE, text)
        dupdate()
    
    def change_scene(self, new_scene_class, **kwargs):
        """Replaces the entire scene stack with a new scene."""
        self._draw_loading_screen()
        while self.scenes:
            self.scenes.pop().destroy()
        
        gc.collect()
        print("+CScene_{}".format(new_scene_class.__name__), gc.mem_free(), " B")

        new_scene = new_scene_class(self, **kwargs)

        self.scenes.append(new_scene)
        new_scene.create()
        print("+CScene: ", gc.mem_free(), " B")


        # Ideally you'd done this :
        # """Stops the current scene and starts a new one."""
        # if self.scenes:
        #     self.scenes[-1].destroy()
        #     self.scenes.pop()
        
        # new_scene = new_scene_class(self, **kwargs)
        # self.scenes.append(new_scene)
        # new_scene.create()
    
    # def change_scene(self, new_scene_class, **kwargs):
    #     """Replaces the current scene with a new one."""
    #     self.pop_scene()
    #     self.push_scene(new_scene_class, **kwargs)
    
    def call_scene(self, new_scene_class, **kwargs):
        # For memory safety, we will treat 'call' like 'change'.
        # A true stack is too risky on this hardware.
        self.change_scene(new_scene_class, **kwargs)

    # def push_scene(self, new_scene_class, **kwargs):
    #     """Helper method to create and add a new scene."""
    #     if self.scenes:
    #         # If there's a scene already, don't destroy it, just pause it.
    #         pass
        
    #     with MemoryProfiler("Scene_{}".format(new_scene_class.__name__)):
    #         new_scene = new_scene_class(self, **kwargs)
    #         self.scenes.append(new_scene)
    #         new_scene.create()

    # def pop_scene(self):
    #     """Removes the top scene from the stack, resuming the one below it."""
    #     if self.scenes:
    #         top_scene = self.scenes.pop()
    #         top_scene.destroy()
    #         del top_scene
    #         gc.collect()
        
        # If the stack becomes empty, the game loop will naturally end.
        if self.scenes:
            self.scenes[-1].resume()
        else:
            # If the stack is empty, the game ends.
            self.running = False


    def return_scene(self):
        # On this device, returning always goes back to the map.
        from cpgame.game_scenes.scene_map import SceneMap
        self.change_scene(SceneMap)
    
    def clear_session(self):
        from cpgame.systems.jrpg import JRPG
        print("Clearing game session data...")
        JRPG.clear()
        # self.session_data.clear()
        gc.collect()