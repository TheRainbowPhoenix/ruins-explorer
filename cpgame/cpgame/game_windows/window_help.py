from cpgame.game_windows.window_base import WindowBase
from gint import *

class WindowHelp(WindowBase):
    def __init__(self):
        super().__init__(0, 0, DWIDTH, 50)
        self._text = ""

    def set_text(self, text: str):
        if self._text != text:
            self._text = text
            self.draw()

    def draw(self):
        if not self.visible: return
        self._draw_skin()
        dtext(self.x + self.padding, self.y + 4, C_BLACK, self._text)