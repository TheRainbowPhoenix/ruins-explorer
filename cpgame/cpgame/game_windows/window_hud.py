# cpgame/game_windows/window_hud.py
# The Heads-Up Display for the map screen.

from gint import *
# from cpgame.game_windows.window_base import WindowBase
from cpgame.systems.jrpg import JRPG

try:
    # This helps with desktop type checking but is ignored on MicroPython
    from typing import Optional
except ImportError:
    pass

# Use const for values that will not change. The compiler can optimize these.
from micropython import const
_HUD_HEIGHT = const(28)
_PADDING = const(8)


class WindowHUD:
    """
    A lightweight, standalone class for drawing the map screen's top HUD.
    It does not inherit from Window_Base to minimize memory and overhead.
    """
    def __init__(self):
        # All layout properties are fixed and can be defined directly.
        self.x = 0
        self.y = 0
        self.width = DWIDTH
        self.height = _HUD_HEIGHT
        self.visible = True
        
        # --- Cached values to prevent recalculation every frame ---
        self._cached_score = -1
        self._cached_gold = -1
        self._cached_day = -1
        
        # Flag to redraw the static parts of the HUD
        self._needs_redraw = True

    def update(self):
        """
        Checks if any data has changed. If so, flags the HUD for a redraw.
        This is more efficient than redrawing every single frame.
        """
        if not JRPG.objects: return

        score = JRPG.objects.variables[1]
        gold = JRPG.objects.party.gold
        day = int(JRPG.objects.timer.total_play_time // 120) + 1

        if (score != self._cached_score or 
            gold != self._cached_gold or 
            day != self._cached_day):
            
            self._cached_score = score
            self._cached_gold = gold
            self._cached_day = day
            self._needs_redraw = True

    def draw(self):
        """Draws the HUD. Only redraws the text if the data has changed."""
        if not self.visible: return
        
        # Only redraw the entire box if necessary (e.g., first frame, or after a menu)
        if self._needs_redraw:
            # --- Draw Window Skin ---
            # This part draws the background box and border.
            drect(self.x, self.y, self.x + self.width - 1, self.y + self.height - 1, C_WHITE)
            drect_border(self.x, self.y, self.x + self.width - 1, self.y + self.height - 1, C_NONE, 1, C_BLACK)
            
            # --- Draw Window Content ---
            if not JRPG.objects: return

            # Draw Score (Variable 1)
            dtext(self.x + _PADDING, self.y + 4, C_BLACK, "Score: " + str(self._cached_score))

            # Draw Gold
            gold_text = str(self._cached_gold) + " G"
            # In-place width calculation: len(text) * 8 (approx char width)
            gold_w = len(gold_text) * 8
            dtext(self.x + self.width - _PADDING - gold_w, self.y + 4, C_BLACK, gold_text)

            # Draw Day
            day_text = "Day " + str(self._cached_day)
            day_w = len(day_text) * 8
            dtext(self.x + (self.width - day_w) // 2, self.y + 4, C_BLACK, day_text)
            
            self._needs_redraw = False
    
    def handle_input(self, input_manager): pass

    def handle_touch(self, x, y): pass