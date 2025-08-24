# cpgame/game_windows/window_number_input.py
import gint
# from cpgame.game_windows.window_base import WindowBase
# import math

try:
    from typing import Optional, Callable
    from cpgame.engine.systems import InputManager
except:
    pass

# Use const for values that will not change. The compiler can optimize these.
from micropython import const
_HEIGHT = const(40)
_PADDING = const(8)
_CHAR_WIDTH = const(18) # Pixel width for each digit character

_BG_COLOR = gint.C_RGB(30, 26, 13)
_BORDER_OUTER_COLOR = gint.C_RGB(18, 10, 2)
_BORDER_INNER_COLOR = gint.C_RGB(29, 22, 8)
_TEXT_COLOR = gint.C_RGB(5, 2, 0)
_SELECT_COLOR = gint.C_RGB(25, 12, 5)


class WindowNumberInput:
    """
    A flat, self-contained modal window for number input.
    Does not inherit from a base class to minimize memory overhead.
    """
    def __init__(self, on_confirm: Callable, on_cancel: Callable):
        # --- State Properties ---
        self.visible = False
        self.active = False
        self._number = 0
        self._digits_max = 1
        self._index = 0  # Cursor position
        
        # --- Callbacks ---
        self._on_confirm = on_confirm
        self._on_cancel = on_cancel
        
        # --- Layout Properties (initialized in start()) ---
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = _HEIGHT

    def destroy(self):
        """Prepares the object for garbage collection by breaking references."""
        self.visible = False
        self.active = False
        self._on_confirm = None
        self._on_cancel = None

    def start(self, initial_number: int, digits_max: int):
        """Initializes the window's state for a new input session."""
        self._digits_max = digits_max
        max_val = (10 ** digits_max) - 1
        self._number = max(0, min(initial_number, max_val))
        self._index = 0
        
        self.width = self._digits_max * 18 + 16 
        self.x = (gint.DWIDTH - self.width) // 2
        self.y = (gint.DHEIGHT - self.height) // 2
        
        self.visible = True
        self.active = True

    def handle_input(self, input_manager: Optional[InputManager]=None):
        """Processes keyboard input to change numbers and confirm/cancel."""
        if not input_manager: return
        if not self.active: return

        if input_manager.is_trigger('confirm'):
            if self._on_confirm:
                self._on_confirm(self._number)
            self.visible = False
            self.active = False
        elif input_manager.is_trigger('cancel'):
            if self._on_cancel:
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
        """Increments or decrements the digit currently under the cursor."""
        place = 10 ** (self._digits_max - 1 - self._index)
        current_digit = (self._number // place) % 10
        self._number -= current_digit * place
        new_digit = (current_digit + amount + 10) % 10
        self._number += new_digit * place

    def update(self):
        """This window's state is entirely driven by external input."""
        pass

    def draw(self):
        """Draws the window skin, numbers, and cursor."""
        if not self.visible: return

        # --- Part 1: Draw Window Skin ---
        gint.drect(self.x, self.y, self.x + self.width - 1, self.y + self.height - 1, _BG_COLOR)
        gint.drect_border(self.x, self.y, self.x + self.width - 1, self.y + self.height - 1, gint.C_NONE, 1, _BORDER_OUTER_COLOR)
        gint.drect_border(self.x + 1, self.y + 1, self.x + self.width - 2, self.y + self.height - 2, gint.C_NONE, 1, _BORDER_INNER_COLOR)

        # --- Part 2: Draw Content ---
        # Draw the numbers, formatted with leading zeros
        number_str = "{:0{width}d}".format(self._number, width=self._digits_max)
        for i, char in enumerate(number_str):
            gint.dtext(self.x + _PADDING + i * _CHAR_WIDTH, self.y + 8, _TEXT_COLOR, char)
            
        # Draw cursor underline
        cursor_x = self.x + _PADDING + self._index * _CHAR_WIDTH
        cursor_y = self.y + self.height - 6
        gint.dline(cursor_x, cursor_y, cursor_x + 16, cursor_y, _SELECT_COLOR)