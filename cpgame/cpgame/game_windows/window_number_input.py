# cpgame/game_windows/window_number_input.py
from gint import *
from cpgame.game_windows.window_base import WindowBase
import math

try:
    from typing import Optional
    from cpgame.engine.systems import InputManager
except:
    pass

class WindowNumberInput(WindowBase):
    def __init__(self, on_confirm, on_cancel):
        self._number = 0
        self._digits_max = 1
        self._index = 0 # Cursor position
        
        width = 0 # Will be set later
        height = 30
        x = (DWIDTH - width) // 2
        y = (DHEIGHT - height) // 2
        
        super().__init__(x, y, width, height)
        self.active = False
        self.visible = False
        self._on_confirm = on_confirm
        self._on_cancel = on_cancel

    def start(self, initial_number: int, digits_max: int):
        self._digits_max = digits_max
        max_val = (10 ** digits_max) - 1
        self._number = max(0, min(initial_number, max_val))
        self._index = 0
        
        self.width = self._digits_max * 18 + self.padding * 2
        self.x = (DWIDTH - self.width) // 2
        
        self.visible = True
        self.active = True

    def handle_input(self, input_manager: Optional[InputManager]=None):
        if not input_manager: return
        if not self.active: return

        if input_manager.interact:
            self._on_confirm(self._number)
            self.visible = False
            self.active = False
        elif input_manager.exit or input_manager.shift:
            self._on_cancel()
        elif input_manager.right:
            self._index = min(self._index + 1, self._digits_max - 1)
        elif input_manager.left:
            self._index = max(self._index - 1, 0)
        elif input_manager.up:
            self._change_digit(1)
        elif input_manager.down:
            self._change_digit(-1)

    def _change_digit(self, amount: int):
        place = 10 ** (self._digits_max - 1 - self._index)
        current_digit = (self._number // place) % 10
        self._number -= current_digit * place
        new_digit = (current_digit + amount + 10) % 10
        self._number += new_digit * place

    def draw(self):
        if not self.visible: return
        super().draw()
        
        # Draw the numbers
        number_str = "{:0{width}d}".format(self._number, width=self._digits_max)
        for i, char in enumerate(number_str):
            dtext(self.x + self.padding + i * 18, self.y + 8, C_BLACK, char)
            
        # Draw cursor
        cursor_x = self.x + self.padding + self._index * 18
        cursor_y = self.y + self.height - 4
        dline(cursor_x, cursor_y, cursor_x + 16, cursor_y, C_BLACK)