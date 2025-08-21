from gint import dclear, dtext, dupdate, dsize, DWIDTH, DHEIGHT, C_BLACK, C_WHITE

try:
    from typing import Optional, List, Set, Tuple,Dict, Any
except:
    pass

from cpgame.engine.scene import Scene
from cpgame.game_windows.window_base import WindowBase

class SceneBase(Scene):
    """A base class for all major scenes, providing a full lifecycle."""
    def __init__(self, game, **kwargs):
        super().__init__(game, **kwargs)
        self._windows: List[WindowBase] = []
        self._active_window: Optional[WindowBase] = None


    def create(self):
        """
        Called once by the game loop when this scene starts.
        Responsible for loading assets and setting up initial state.
        """
        self._windows = []
        self._active_window = None

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

            return "FOCUS"

        # ...

        return None

    def draw(self, frame_time_ms: int):
        # Draw all windows on top
        for window in self._windows:
            window.draw()
    

    
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

class SceneMenuBase(SceneBase):
    pass