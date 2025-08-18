# cpgame/game_windows/window_selectable.py
# A base class for windows that have a selectable cursor.

from gint import *
from cpgame.game_windows.window_base import WindowBase

try:
    from typing import Dict, Any, Callable, Optional
    from cpgame.engine.systems import InputManager
except: pass

class WindowSelectable(WindowBase):
    """A base class for windows that have a selectable grid cursor."""
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self._index = -1
        self._handlers: Dict[str, Callable] = {}
        self.active = False

    def activate(self): self.active = True
    def deactivate(self): self.active = False

    @property
    def index(self) -> int:
        return self._index

    @index.setter
    def index(self, value: int):
        self._index = value
        # In a full engine, this would call a refresh_cursor method
    
    def set_handler(self, symbol: str, method: Callable):
        """Assigns a callback method to a symbol (e.g., 'ok', 'cancel')."""
        self._handlers[symbol] = method

    def call_handler(self, symbol: str, *args):
        """Calls the handler associated with a symbol if it exists."""
        if symbol in self._handlers:
            self._handlers[symbol](*args)
    
    # Input handling will be specific to each subclass
    def handle_input(self, input_manager: Optional[InputManager]): 
        if not self.active or not input_manager:
            return
            
        if input_manager.interact:
            self.call_handler('ok')
        elif input_manager.exit:
            self.call_handler('cancel')

    def handle_touch(self, x, y): pass # TODO ??

    def update(self):
        pass