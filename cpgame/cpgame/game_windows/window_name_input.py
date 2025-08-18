# cpgame/game_windows/window_name_input.py
from gint import *
from cpgame.game_windows.window_selectable import WindowSelectable

try:
    from typing import Optional
    from cpgame.engine.systems import InputManager
except:
    pass

class WindowNameInput(WindowSelectable):
    """The virtual keyboard for name input."""
    LATIN1 = [
        'A','B','C','D','E',  'F','G','H','I','J',
        'a','b','c','d','e',  'f','g','h','i','j',
        'K','L','M','N','O',  'k','l','m','n','o',
        'P','Q','R','S','T',  'p','q','r','s','t',
        'U','V','W','X','Y',  'u','v','w','x','y',
        'Z','0','1','2','3',  'z','4','5','6','7',
        ' ',' ',' ',' ',' ',  ' ',' ',' ',' ',' ',
        '!','@','#','$','%',  '^','&','*','(',')',
        '-','_','=','+',' ',  ' ','Bksp', ' ','OK',' '
    ]
    
    def __init__(self, edit_window):
        width = 320
        height = 150
        x = (DWIDTH - width) // 2
        y = edit_window.y + edit_window.height + 4
        super().__init__(x, y, width, height)

        self._edit_window = edit_window
        self.index = 0
        self.visible = False
        self.active = False
        self.col_max = 10
        self.row_max = 9
        self._cell_width = self.width // self.col_max
        self._cell_height = self.height // self.row_max

    def start(self, edit_window):
        self._edit_window = edit_window
        self.index = 0
        
        self.visible = True
        self.active = True

    def character(self) -> str:
        return self.LATIN1[self.index]

    def handle_input(self, input_manager: Optional[InputManager]=None):
        if not input_manager: return
        if not self.active: return
        
        # Cursor movement
        if input_manager.down:
            self.index = (self.index + self.col_max) % (self.col_max * self.row_max)
        if input_manager.up:
            self.index = (self.index - self.col_max + (self.col_max * self.row_max)) % (self.col_max * self.row_max)
        if input_manager.right:
            self.index = (self.index + 1) % (self.col_max * self.row_max)
        if input_manager.left:
            self.index = (self.index - 1 + (self.col_max * self.row_max)) % (self.col_max * self.row_max)

        if input_manager.interact:
            self._process_ok()
        if input_manager.exit:
            self._process_backspace() # Let's use EXIT for backspace

    def handle_touch(self, touch_x, touch_y):
        if not self.active or not self.visible: return
        
        # Check if touch is inside the window
        if self.x <= touch_x < self.x + self.width and self.y <= touch_y < self.y + self.height:
            col = (touch_x - self.x) // self._cell_width
            row = (touch_y - self.y) // self._cell_height
            self.index = row * self.col_max + col
            self._process_ok()

    def _process_ok(self):
        char = self.character()
        if char == 'OK':
            self.call_handler('ok', self._edit_window.name)
        elif char == 'Bksp':
            self._process_backspace()
        else:
            self._edit_window.add(char)
            
    def _process_backspace(self):
        self._edit_window.back()

    def draw(self):
        if not self.visible: return
        super().draw()
        
        for i, char in enumerate(self.LATIN1):
            x = self.x + (i % self.col_max) * self._cell_width + 8
            y = self.y + (i // self.col_max) * self._cell_height
            dtext(x, y, C_BLACK, char)
            
        # Draw cursor
        cursor_x = self.x + (self.index % self.col_max) * self._cell_width
        cursor_y = self.y + (self.index // self.col_max) * self._cell_height
        drect_border(cursor_x, cursor_y, cursor_x + self._cell_width, cursor_y + self._cell_height, C_NONE, 1, C_BLUE)