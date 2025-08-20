# engine/game.py
# The main game class with the fixed-timestep loop and scene management.

import time
import gc # Import garbage collector for cleanup
from gint import *
from cpgame.engine.scene import Scene
from cpgame.engine.assets import AssetManager
from cpgame.game_scenes.menu_scene import MenuScene # TODO: should be dynamic ?

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
        self.running: bool = False
        self.fixed_timestep: float = 0.055
        self.frame_cap_ms: int = 53

        # Generic container for game-mode-specific systems.
        self.session_data: Dict[str, Any] = {}

    def start(self, initial_scene_class):
        """Initializes assets and starts the game with the first scene."""
        self.assets.load_all()
        self.running = True
        self.push_scene(initial_scene_class)

        while self.running and self.scenes:
            frame_start_time = time.ticks_ms()
            current_scene = self.scenes[-1]

            # --- LOGIC UPDATE ---
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
    
    def change_scene(self, new_scene_class, **kwargs):
        """Stops the current scene and starts a new one."""
        if self.scenes:
            self.scenes[-1].destroy()
            self.scenes.pop()
        
        new_scene = new_scene_class(self, **kwargs)
        self.scenes.append(new_scene)
        new_scene.create()
    
    # def change_scene(self, new_scene_class, **kwargs):
    #     """Replaces the current scene with a new one."""
    #     self.pop_scene()
    #     self.push_scene(new_scene_class, **kwargs)

    def push_scene(self, new_scene_class, **kwargs):
        """Adds a new scene to the top of the stack and makes it active."""
        if self.scenes:
            # If there's a scene already, don't destroy it, just pause it.
            pass
        
        new_scene = new_scene_class(self, **kwargs)
        self.scenes.append(new_scene)
        new_scene.create()

    def pop_scene(self):
        """Removes the top scene from the stack, resuming the one below it."""
        if self.scenes:
            top_scene = self.scenes.pop()
            top_scene.destroy()
        
        # If the stack becomes empty, the game loop will naturally end.
        if self.scenes:
            self.scenes[-1].resume()
        else:
            # If the stack is empty, the game ends.
            self.running = False

    def clear_session(self):
        from cpgame.systems.jrpg import JRPG
        print("Clearing game session data...")
        JRPG.clear()
        self.session_data.clear()
        gc.collect()