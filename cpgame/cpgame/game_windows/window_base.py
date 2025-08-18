# cpgame/game_windows/window_base.py
# The superclass for all window objects in the game.

from gint import drect, drect_border, C_WHITE, C_BLACK, C_NONE

try:
    from typing import Optional
except:
    pass

class WindowBase:
    """A base class for drawable UI elements."""
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.visible = True
        self.padding = 8

    def _draw_skin(self):
        """Draws the default white window with a black border."""
        if self.visible:
            drect(self.x, self.y, self.x + self.width - 1, self.y + self.height - 1, C_WHITE)
            drect_border(self.x, self.y, self.x + self.width - 1, self.y + self.height - 1, C_NONE, 1, C_BLACK)

    def update(self):
        """Update logic for the window (e.g., animations, state)."""
        pass

    def draw(self):
        """Draws the window skin. Subclasses should call super().draw() first."""
        if self.visible:
            self._draw_skin()
    