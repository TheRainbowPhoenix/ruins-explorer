from gint import *
from cpgame.game_windows.window_base import WindowBase

class WindowNameEdit(WindowBase):
    """Displays the name being edited."""
    def __init__(self, actor, max_char):
        width = 300
        height = 60
        x = (DWIDTH - width) // 2
        y = (DHEIGHT - height - 160) // 2 # Position above keyboard
        super().__init__(x, y, width, height)
    
        self._actor = actor
        self._max_char = max_char
        if actor:
            self._name = actor.name[:self._max_char]
        else:
            self._name = ""
        self._index = len(self._name)
        self.visible = False
        
    @property
    def name(self) -> str: return self._name

    def add(self, char: str) -> bool:
        if self._index < self._max_char:
            self._name += char
            self._index += 1
            return True
        return False

    def back(self) -> bool:
        if self._index > 0:
            self._index -= 1
            self._name = self._name[:self._index]
            return True
        return False

    def draw(self):
        if not self.visible: return
        super().draw()
        
        char_width = 14 # Approximate width of a character
        
        # Draw underlines
        for i in range(self._max_char):
            ux = self.x + self.padding + i * char_width
            uy = self.y + self.height - 12
            dline(ux, uy, ux + 12, uy, C_BLACK)

        # Draw characters
        for i, char in enumerate(self._name):
            dtext(self.x + self.padding + i * char_width, self.y + 8, C_BLACK, char)
            
        # Draw cursor
        cursor_x = self.x + self.padding + self._index * char_width
        drect_border(cursor_x - 1, self.y + 7, cursor_x + 12, self.y + 25, C_NONE, 1, C_BLUE)