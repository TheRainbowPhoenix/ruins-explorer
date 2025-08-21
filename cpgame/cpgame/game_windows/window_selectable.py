# cpgame/game_windows/window_selectable.py
# A base class for windows that have a selectable cursor.

from gint import *
from cpgame.game_windows.window_base import WindowBase
from cpgame.engine.geometry import Rect

try:
    from typing import Dict, Callable, Optional, List
    from cpgame.engine.systems import InputManager
except: pass

class WindowSelectable(WindowBase):
    """A base class for windows that have a selectable grid cursor."""
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self._index = -1
        self._handlers: Dict[str, Callable] = {}
        self._help_window = None
        self._cursor_fix: bool = False
        self._cursor_all: bool = False
        self.active: bool = False
        self.padding_bottom = 0
        self.oy = None

        # Cursor rectangle (used for visual cursor or clipping)
        self.cursor_rect = Rect(0, 0, 0, 0)

        # Setup padding and layout
        self.update_padding()
    
    def _set_index(self, value: int):
        """Internal index setter to avoid potential recursion in subclasses."""
        if self._index != value:
            self._index = value

    @property
    def index(self) -> int:
        return self._index

    @index.setter
    def index(self, value: int):
        self._index = value
        self.update_cursor()
        self.call_update_help()

    @property
    def help_window(self):
        return self._help_window

    @help_window.setter
    def help_window(self, window):
        self._help_window = window
        self.call_update_help()

    @property
    def cursor_fix(self) -> bool:
        return self._cursor_fix

    @cursor_fix.setter
    def cursor_fix(self, value: bool):
        self._cursor_fix = value
        self.update_cursor()

    @property
    def cursor_all(self) -> bool:
        return self._cursor_all

    @cursor_all.setter
    def cursor_all(self, value: bool):
        self._cursor_all = value
        self.update_cursor()

    # -------------------------------------------------------------------------
    # Layout Configuration (Override in subclasses)
    # -------------------------------------------------------------------------

    @property
    def col_max(self) -> int:
        """Number of columns in grid layout."""
        return 1

    @property
    def spacing(self) -> int:
        """Spacing between items."""
        return 32

    @property
    def item_max(self) -> int:
        """Number of items (must be implemented by subclasses)."""
        return 0

    @property
    def item_width(self) -> float:
        """Width of a single item."""
        return (self.width - self.standard_padding * 2 + self.spacing) / self.col_max - self.spacing

    @property
    def item_height(self) -> int:
        """Height of a single item."""
        return self.line_height

    @property
    def row_max(self) -> int:
        """Number of rows needed to display all items."""
        if self.col_max == 0:
            return 1
        return max(1, (self.item_max + self.col_max - 1) // self.col_max)

    @property
    def contents_height(self) -> int:
        """Ensure content height is multiple of item_height."""
        base = super().contents_height
        item_h = self.item_height
        return max(base - (base % item_h), self.row_max * item_h)
    
    def update_padding_bottom(self):
        surplus = (self.height - self.standard_padding * 2) % self.item_height
        self.padding_bottom = self.padding + surplus

    # -------------------------------------------------------------------------
    # Scrolling & Row Management
    # -------------------------------------------------------------------------

    @property
    def top_row(self) -> int:
        """Current top visible row (based on oy)."""
        oy = self.oy or (self.row_max-1) * self.item_height
        return oy // self.item_height

    @top_row.setter
    def top_row(self, row: int):
        row = max(0, min(row, self.row_max - 1))
        self.oy = row * self.item_height

    @property
    def bottom_row(self) -> int:
        """Bottom visible row."""
        return self.top_row + self.page_row_max - 1

    @bottom_row.setter
    def bottom_row(self, row: int):
        self.top_row = row - (self.page_row_max - 1)

    @property
    def page_row_max(self) -> int:
        """Number of rows visible per page."""
        available = self.height - self.padding - self.padding_bottom
        return available // self.item_height if self.item_height > 0 else 1

    @property
    def page_item_max(self) -> int:
        """Number of items per page."""
        return self.page_row_max * self.col_max

    def horizontal(self) -> bool:
        """True if only one row is visible (horizontal layout)."""
        return self.page_row_max == 1

    # -------------------------------------------------------------------------
    # Index & Cursor Utilities
    # -------------------------------------------------------------------------

    def row(self) -> int:
        """Current row of the cursor."""
        return self.index // self.col_max if self.index >= 0 else 0

    def select(self, index: Optional[int]):
        """Select an item by index."""
        if index is not None:
            self.index = index

    def unselect(self):
        """Deselect all items."""
        self.index = -1

    def ensure_cursor_visible(self):
        """Scroll so the current item is visible."""
        if self.index < 0:
            return
        if self.row() < self.top_row:
            self.top_row = self.row()
        elif self.row() > self.bottom_row:
            self.bottom_row = self.row()

    def update_cursor(self):
        """Update the cursor rectangle based on current state."""
        if self._cursor_all:
            h = self.row_max * self.item_height
            self.cursor_rect = Rect(0, 0, self.width, h)
            self.top_row = 0
        elif self.index < 0:
            self.cursor_rect = Rect(0, 0, 0, 0)
        else:
            self.ensure_cursor_visible()
            self.cursor_rect = self.item_rect(self.index).copy()

    # -------------------------------------------------------------------------
    # Geometry: Item Rectangles
    # -------------------------------------------------------------------------

    def item_rect(self, index: int) -> Rect:
        """Get the rectangle for the item at given index."""
        x = (index % self.col_max) * (self.item_width + self.spacing)
        y = (index // self.col_max) * self.item_height
        w = self.item_width
        h = self.item_height
        return Rect(int(x), int(y), int(w), int(h))

    def item_rect_for_text(self, index: int) -> Rect:
        """Get inner rectangle for drawing text (with padding)."""
        rect = self.item_rect(index)
        return Rect(rect.x + 4, rect.y, rect.width - 8, rect.height)

    # -------------------------------------------------------------------------
    # Input Handling
    # -------------------------------------------------------------------------

    def cursor_movable(self) -> bool:
        """Check if cursor can be moved."""
        return (self.active and self.visible and
                not self._cursor_fix and not self._cursor_all and
                self.item_max > 0)

    def cursor_down(self, wrap: bool = False):
        if self.index < self.item_max - self.col_max or (wrap and self.col_max == 1):
            self.select((self.index + self.col_max) % self.item_max)

    def cursor_up(self, wrap: bool = False):
        if self.index >= self.col_max or (wrap and self.col_max == 1):
            self.select((self.index - self.col_max + self.item_max) % self.item_max)

    def cursor_right(self, wrap: bool = False):
        if self.col_max >= 2 and (self.index < self.item_max - 1 or (wrap and self.horizontal())):
            self.select((self.index + 1) % self.item_max)

    def cursor_left(self, wrap: bool = False):
        if self.col_max >= 2 and (self.index > 0 or (wrap and self.horizontal())):
            self.select((self.index - 1 + self.item_max) % self.item_max)

    def cursor_pagedown(self):
        if self.top_row + self.page_row_max < self.row_max:
            self.top_row += self.page_row_max
            self.select(min(self.index + self.page_item_max, self.item_max - 1))

    def cursor_pageup(self):
        if self.top_row > 0:
            self.top_row -= self.page_row_max
            self.select(max(self.index - self.page_item_max, 0))

    def process_cursor_move(self, inp: InputManager):
        """Handle cursor movement via input."""
        if not self.cursor_movable():
            return

        last_index = self.index


        if inp.is_repeat('down'):
            self.cursor_down(inp.is_trigger('down'))
        if inp.is_repeat('up'):
            self.cursor_up(inp.is_trigger('up'))
        if inp.is_repeat('right'):
            self.cursor_right(inp.is_trigger('right'))
        if inp.is_repeat('left'):
            self.cursor_left(inp.is_trigger('left'))

        # Page up/down
        if inp.is_trigger('page_down') and not self.handle('pagedown'):
            self.cursor_pagedown()
        if inp.is_trigger('page_up') and not self.handle('pageup'):
            self.cursor_pageup()

        # Play sound if index changed
        # if self.index != last_index:
        #     Sound.play_cursor()

    def ok_enabled(self) -> bool:
        """Check if OK handler is set."""
        return self.handle('ok')

    def cancel_enabled(self) -> bool:
        """Check if Cancel handler is set."""
        return self.handle('cancel')

    def process_ok(self):
        if self.current_item_enabled():
            # Sound.play_ok()
            self.deactivate()
            self.call_ok_handler()
        else:
            pass
            # Sound.play_buzzer()

    def call_ok_handler(self):
        self.call_handler('ok')

    def process_cancel(self):
        # Sound.play_cancel()
        self.deactivate()
        self.call_cancel_handler()

    def call_cancel_handler(self):
        self.call_handler('cancel')

    def process_pageup(self):
        # Sound.play_cursor()
        self.deactivate()
        self.call_handler('pageup')

    def process_pagedown(self):
        # Sound.play_cursor()
        self.deactivate()
        self.call_handler('pagedown')

    def process_handling(self, inp: InputManager):
        """Process OK, Cancel, Page Up/Down."""
        
        if not self.visible or not self.active:
            return

        if self.ok_enabled() and inp.is_trigger('confirm'):
            self.process_ok()
        elif self.cancel_enabled() and inp.is_trigger('cancel'):
            self.process_cancel()
        elif self.handle('pagedown') and inp.is_trigger('page_down'):
            self.process_pagedown()
        elif self.handle('pageup') and inp.is_trigger('page_up'):
            self.process_pageup()

    def update(self):
        """Frame update: handle movement and input."""
        super().update()
        # self.process_cursor_move()
        # self.process_handling()
        
    # -------------------------------------------------------------------------
    # Handlers
    # -------------------------------------------------------------------------

    def set_handler(self, symbol: str, method: Callable):
        """Assign a callback to a symbol (e.g., 'ok', 'cancel')."""
        self._handlers[symbol] = method

    def handle(self, symbol: str) -> bool:
        """Check if a handler exists for the symbol."""
        return symbol in self._handlers and self._handlers[symbol] is not None

    # Input handling will be specific to each subclass
    def handle_input(self, input_manager: Optional[InputManager]): 
        if not self.active or not input_manager:
            return
        
        self.process_handling(input_manager)
        self.process_cursor_move(input_manager)
            
        # if input_manager.interact:
        #     self.call_handler('ok')
        # elif input_manager.exit:
        #     self.call_handler('cancel')

    def handle_touch(self, x, y): pass # TODO ??


    def call_handler(self, symbol: str, *args):
        """Call the handler for the given symbol."""
        if self.handle(symbol):
            self._handlers[symbol](*args)

    # -------------------------------------------------------------------------
    # Help Window Integration
    # -------------------------------------------------------------------------

    def call_update_help(self):
        """Call update_help if active and help window exists."""
        if self.active and self._help_window:
            self.update_help()

    def update_help(self):
        """Override to update help window text."""
        if self._help_window:
            self._help_window.clear()

    # -------------------------------------------------------------------------
    # Item Drawing
    # -------------------------------------------------------------------------

    def current_item_enabled(self) -> bool:
        """Override in subclasses to enable/disable selection."""
        return True

    def draw_item(self, index: int):
        """Override to draw individual items."""
        pass

    def draw_all_items(self):
        """Draw all items."""
        for i in range(self.item_max):
            self.draw_item(i)

    def clear_item(self, index: int):
        """Erase the content of an item."""
        rect = self.item_rect(index)
        drect(rect.x, rect.y, rect.width, rect.height, C_WHITE)

    def redraw_item(self, index: int):
        """Redraw a single item."""
        if index >= 0:
            self.clear_item(index)
            self.draw_item(index)

    def redraw_current_item(self):
        """Redraw the currently selected item."""
        self.redraw_item(self.index)

    # -------------------------------------------------------------------------
    # Refresh
    # -------------------------------------------------------------------------

    def draw(self):
        """Draws the window skin. Subclasses should call super().draw() first."""
        super().draw()
        self.draw_all_items()
        self.update_cursor()

    def refresh(self):
        """Refresh the window contents."""
        self.draw_all_items()
        self.update_cursor()