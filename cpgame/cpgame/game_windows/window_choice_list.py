# cpgame/game_windows/window_choice_list.py
from gint import *
from cpgame.systems.jrpg import JRPG
from cpgame.game_windows.window_selectable import WindowSelectable

try:
    from typing import Optional, List
    from cpgame.engine.systems import InputManager
except:
    pass


class WindowChoiceList(WindowSelectable):
    def __init__(self, message_window):
        # Store a reference to the main message window for positioning
        self._message_window = message_window
        # Initial dummy size
        super().__init__(0, 0, 120, 40)
        self._choices = []
        self.openness = 0
        self.visible = False
        self.active = False

    def start(self, choices: List[str], cancel_type=0, callback=None):
        self._choices = choices

        def var_then_callback(code: Optional[int]=None):
            if JRPG.objects and JRPG.objects.message and JRPG.objects.message.choice_variable_id is not None:
                JRPG.objects.variables[JRPG.objects.message.choice_variable_id] = code + 1 if code is not None else None
            if callback:
                callback(code)

        self._cancel_type = cancel_type
        if callback:
            self.set_handler('ok', lambda i: var_then_callback(i))
            # Handle cancel based on rules
            if cancel_type == -2: # Disallow
                self.set_handler('cancel', lambda i: var_then_callback())
            elif cancel_type == -1: # Branch
                self.set_handler('cancel', lambda i: var_then_callback(-1))
            else: # Specific choice index
                self.set_handler('cancel', lambda i: var_then_callback(cancel_type))
        
        self.update_placement()
        self.create_contents() # Recreate contents with new size
        
        self.index = 0
        self.openness = 255
        self.visible = True
        
        self.activate()
        self.refresh()

    def update_placement(self):
        """Positions the window based on the main message window's location."""
        # Calculate width based on the longest choice text
        max_width = 96
        for choice in self._choices:
            # A simple approximation for text width
            text_w = len(choice) * 8 # Simple width approximation
            if text_w > max_width:
                max_width = text_w
        self.width = max_width + self.padding * 2

        self.height = len(self._choices) * 24 + self.padding * 2
        
        # Position to the right, avoiding the message window
        self.x = DWIDTH - self.width
        # If the message window is in the bottom half of the screen, place this window above it.
        if self._message_window.y >= DHEIGHT / 2:
            self.y = self._message_window.y - self.height
        else: # Otherwise, place it below.
            self.y = self._message_window.y + self._message_window.height

    def handle_input(self, input_manager: Optional[InputManager]=None):
        if not self.active: return
        if not input_manager: return
        last_index = self.index
        
        if input_manager.up: self.index = (self.index - 1 + self.item_max) % self.item_max
        if input_manager.down: self.index = (self.index + 1) % self.item_max
        
        if self.index != last_index: self.refresh()
            
        if input_manager.interact: self.call_handler('ok', self.index)
        if input_manager.exit: self.call_handler('cancel')
    
    def draw(self):
        if not self.visible: return
        self._draw_skin() # From Window_Base
        for i, choice in enumerate(self._choices):
            dtext(self.x + self.padding, self.y + self.padding + i * 24, C_BLACK, choice)
        
        # Draw cursor
        if self.index >= 0:
            cursor_y = self.y + self.padding + self.index * 24
            drect_border(self.x + 4, cursor_y - 2, self.x + self.width - 4, cursor_y + 20, C_NONE, 1, C_BLUE)

    @property
    def item_max(self) -> int:
        return len(self._choices)

    def draw_item(self, index):
        """Draws a single choice text."""
        dtext(self.x + self.padding, self.y + self.padding + index * 24, C_BLACK, self._choices[index])

    def refresh(self):
        """Draws all choices and the cursor."""
        if not self.visible: return
        self._draw_skin()
        for i in range(len(self._choices)):
            self.draw_item(i)
        
        # Draw cursor
        cursor_y = self.y + self.padding + self.index * 24
        drect_border(self.x + 4, cursor_y - 2, self.x + self.width - 4, cursor_y + 20, C_NONE, 1, C_BLUE)