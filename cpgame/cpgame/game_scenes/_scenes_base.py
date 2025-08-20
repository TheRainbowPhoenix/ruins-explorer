try:
    from typing import Optional, List, Set, Tuple,Dict, Any
except:
    pass

from cpgame.engine.scene import Scene
from cpgame.game_windows.window_base import WindowBase

class SceneBase(Scene):

    def create(self):
        """
        Called once by the game loop when this scene starts.
        Responsible for loading assets and setting up initial state.
        """
        self._windows = []
        self._active_window: Optional[WindowBase] = None

    def update(self, dt: float) -> Optional[str]:
        """
        Main logic update, called every fixed timestep.
        """
        # First, poll the input state for this frame
        self.input.update()

        # Update all windows
        for window in self._windows:
            window.update()
        
        # --- INPUT & LOGIC PHASE ---
        if self._active_window:
            # If a modal window is active, it gets all input
            self._active_window.handle_input(self.input) # update ? handle_input ?
            # Add touch handling placeholder
            # touch = get_touch_event() 
            # if touch: self._active_window.handle_touch(touch.x, touch.y)

            return None

        return None
        



    def draw(self, frame_time_ms: int):
        # Draw all windows on top
        for window in self._windows:
            window.draw()
    

class SceneMenuBase(SceneBase):
    pass