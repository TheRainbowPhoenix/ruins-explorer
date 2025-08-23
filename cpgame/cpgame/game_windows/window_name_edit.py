import gint
try:
    # This helps with desktop type checking but is ignored on MicroPython
    from typing import Optional, Any
except ImportError:
    pass

# Use const for values that will not change, allowing compiler optimizations.
from micropython import const
_WIDTH = const(300)
_HEIGHT = const(60)
_PADDING = const(8)
_CHAR_WIDTH = const(14) # The pixel width allocated for each character.


class WindowNameEdit:
    """
    Displays the name being edited. This is a flat class with no inheritance
    for maximum memory efficiency. Its state is controlled by WindowNameInput.
    """
    def __init__(self):
        # --- Layout Properties ---
        # The window is positioned to appear above the virtual keyboard.
        # Height of keyboard (150) + padding (4) = 154
        self.x = (gint.DWIDTH - _WIDTH) // 2
        self.y = (gint.DHEIGHT - _HEIGHT - 154) // 2
        self.width = _WIDTH
        self.height = _HEIGHT
        
        # --- State Properties ---
        self.visible = False
        self._actor: Optional[Any] = None
        self._max_char = 0
        self._name = ""
        self._index = 0

    def start(self, actor: Any, max_char: int):
        """
        Initializes the window's state for a new editing session.
        Called by the scene right before making the window visible.
        """
        self._actor = actor
        self._max_char = max_char
        self._name = actor.name[:self._max_char] if actor else ""
        self._index = len(self._name)
        self.visible = True
        
    @property
    def name(self) -> str:
        """Returns the current name string being edited."""
        return self._name

    def add(self, char: str) -> bool:
        """Adds a character to the name if there is space."""
        if self._index < self._max_char:
            self._name += char
            self._index += 1
            return True
        return False

    def back(self) -> bool:
        """Removes the last character from the name."""
        if self._index > 0:
            self._index -= 1
            self._name = self._name[:self._index]
            return True
        return False

    def update(self):
        """This window has no internal logic that needs to run every frame."""
        pass

    def draw(self):
        """Draws the entire window, including skin, underlines, text, and cursor."""
        if not self.visible:
            return

        # --- Part 1: Draw Window Skin ---
        # This draws the background box and border.
        gint.drect(self.x, self.y, self.x + self.width - 1, self.y + self.height - 1, gint.C_WHITE)
        gint.drect_border(self.x, self.y, self.x + self.width - 1, self.y + self.height - 1, gint.C_NONE, 1, gint.C_BLACK)

        # --- Part 2: Draw Window Content ---
        
        # Draw underlines for each character slot
        for i in range(self._max_char):
            ux = self.x + _PADDING + i * _CHAR_WIDTH
            uy = self.y + self.height - 12
            gint.dline(ux, uy, ux + 12, uy, gint.C_BLACK)

        # Draw characters
        for i, char in enumerate(self._name):
            gint.dtext(self.x + _PADDING + i * _CHAR_WIDTH, self.y + 8, gint.C_BLACK, char)
            
        # Draw cursor
        cursor_x = self.x + _PADDING + self._index * _CHAR_WIDTH
        gint.drect_border(cursor_x - 1, self.y + 7, cursor_x + 12, self.y + 25, gint.C_NONE, 1, gint.C_BLUE)
    
    def destroy(self):
        """
        Explicitly releases references to prepare for garbage collection.
        This is important for breaking the reference to the actor object.
        """
        self.visible = False
        self._actor = None
        self._name = ""

        del self.x
        del self.y
        del self.width
        del self.height
        del self.visible
        del self._actor
        del self._max_char
        del self._name
        del self._index