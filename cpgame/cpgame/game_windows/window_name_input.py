# cpgame/game_windows/window_name_input.py
import gint
# from cpgame.game_windows.window_selectable import WindowSelectable

try:
    from typing import Optional, Callable, Any, Dict
    from cpgame.engine.systems import InputManager
    from .window_name_edit import WindowNameEdit
except:
    pass

from micropython import const
_WIDTH = const(320)
_HEIGHT = const(150)
_COLS = const(10)
_ROWS = const(9)

# Custom window colors
_BG_COLOR = gint.C_RGB(30, 26, 13)
_BORDER_OUTER_COLOR = gint.C_RGB(18, 10, 2)
_BORDER_INNER_COLOR = gint.C_RGB(29, 22, 8)
_TEXT_COLOR = gint.C_RGB(5, 2, 0)
_SELECT_COLOR = gint.C_RGB(25, 12, 5)


class WindowNameInput:
    """
    The virtual keyboard for name input. This is a flat class with no
    complex inheritance to minimize memory overhead.
    """
    # Character layout for the virtual keyboard
    LATIN1 = [
        'A','B','C','D','E',  'F','G','H','I','J',
        'a','b','c','d','e',  'f','g','h','i','j',
        'K','L','M','N','O',  'k','l','m','n','o',
        'P','Q','R','S','T',  'p','q','r','s','t',
        'U','V','W','X','Y',  'u','v','w','x','y',
        'Z','0','1','2','3',  'z','4','5','6','7',
        ' ','-','_','[',']',  '!','@','#','$','%',
        '^','&','*','(',')',  '=','+','/','~',';',
        'Bksp',' ',' ',' ',' ',  ' ',' ', ' ',' ','OK'
    ]
    
    def __init__(self):
        # --- State Properties ---
        self.visible = False
        self.active = False
        self._edit_window: Optional['WindowNameEdit'] = None
        self._handlers: Dict[str, Callable] = {}
        self.index = 0
        
        # --- Layout (calculated once) ---
        # The keyboard is positioned relative to where the edit window will be.
        # Edit window Y is (DHEIGHT - 60 - 154) // 2
        edit_window_bottom_y = ((gint.DHEIGHT - 60 - 154) // 2) + 60
        self.x = (gint.DWIDTH - _WIDTH) // 2
        self.y = edit_window_bottom_y + 4
        self.width = _WIDTH
        self.height = _HEIGHT
        
        self._cell_width = self.width // _COLS
        self._cell_height = self.height // _ROWS
        
    def destroy(self):
        """Prepares the object for garbage collection by breaking references."""
        self.visible = False
        self.active = False
        self._edit_window = None
        self._handlers.clear()

        del self._edit_window
        del self._handlers

    def set_handler(self, symbol: str, method: Callable):
        """Assigns a callback method for 'ok' or 'cancel' events."""
        self._handlers[symbol] = method

    def start(self, edit_window: 'WindowNameEdit'):
        """Initializes the keyboard for a new editing session."""
        self._edit_window = edit_window
        self.index = 0
        self.visible = True
        self.active = True

    def character(self) -> str:
        return self.LATIN1[self.index]

    def handle_input(self, input_manager: Optional[InputManager]=None):
        if not input_manager: return
        if not self.active: return
        
        last_index = self.index
        
        if input_manager.down:
            self.index = (self.index + _COLS) % (_COLS * _ROWS)
        if input_manager.up:
            self.index = (self.index - _COLS + (_COLS * _ROWS)) % (_COLS * _ROWS)
        if input_manager.right:
            self.index = (self.index + 1) % (_COLS * _ROWS)
        if input_manager.left:
            self.index = (self.index - 1 + (_COLS * _ROWS)) % (_COLS * _ROWS)

        if input_manager.interact:
            self._process_ok()
        if input_manager.is_trigger('cancel'):
            self._process_backspace() # Let's use EXIT for backspace

    def handle_touch(self, touch_x: int, touch_y: int):
        """Processes a touch event on the virtual keyboard."""
        if not self.active or not self.visible: return
        
        # Check if touch is inside the window
        if self.x <= touch_x < self.x + self.width and self.y <= touch_y < self.y + self.height:
            col = (touch_x - self.x) // self._cell_width
            row = (touch_y - self.y) // self._cell_height
            self.index = row * _COLS + col
            self._process_ok()

    def _process_ok(self):
        """Handles the action for the currently selected key."""
        char = self.LATIN1[self.index]
        if char == 'OK':
            if self._edit_window and 'ok' in self._handlers:
                self._handlers['ok'](self._edit_window.name)
        elif char == 'Bksp':
            self._process_backspace()
        elif char != ' ': # Ignore empty buttons
            if self._edit_window:
                self._edit_window.add(char)
            
    def _process_backspace(self):
        if self._edit_window:
            self._edit_window.back()

    def update(self):
        """This window's state is entirely driven by external input."""
        pass

    def draw(self):
        """Draws the virtual keyboard, its characters, and the cursor."""
        if not self.visible: return

        # Draw window skin
        gint.drect(self.x, self.y, self.x + self.width - 1, self.y + self.height - 1, _BG_COLOR)
        gint.drect_border(self.x, self.y, self.x + self.width, self.y + self.height, gint.C_NONE, 1, _BORDER_OUTER_COLOR)
        gint.drect_border(self.x+1, self.y+1, self.x + self.width - 1, self.y + self.height - 1, gint.C_NONE, 1, _BORDER_INNER_COLOR)
        
        # Draw all characters on the keyboard
        for i, char in enumerate(self.LATIN1):
            if char != ' ':
                col = i % _COLS
                row = i // _COLS
                char_x = self.x + col * self._cell_width + 8
                char_y = self.y + row * self._cell_height + 2
                gint.dtext(char_x, char_y, _TEXT_COLOR, char)
            
        # Draw the selection cursor
        cursor_x = self.x + (self.index % _COLS) * self._cell_width
        cursor_y = self.y + (self.index // _COLS) * self._cell_height
        gint.drect_border(cursor_x, cursor_y, cursor_x + self._cell_width - 1, cursor_y + self._cell_height - 1, gint.C_NONE, 2, _SELECT_COLOR)