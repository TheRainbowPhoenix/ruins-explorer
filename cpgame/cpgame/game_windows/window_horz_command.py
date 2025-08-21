# cpgame/game_windows/window_horz_command.py
from cpgame.engine.geometry import Rect
from cpgame.game_windows.window_command import WindowCommand
from gint import dtext, C_BLACK, C_DARK  # Assuming C_DARK for disabled

try:
    from typing import Optional, Tuple
except:
    pass

class WindowHorzCommand(WindowCommand):
    """
    A horizontally arranged command window.
    Displays a single row of commands with optional horizontal scrolling.
    """

    def __init__(self, x: int, y: int, width: Optional[int] = None, height: Optional[int] = None):
        self.ox = 0
        super().__init__(x, y, width or self.window_width(), height or self.window_height())

    # Window Dimensions and Layout

    def visible_line_number(self) -> int:
        """Always one row in horizontal layout."""
        return 1

    @property
    def col_max(self) -> int:
        """Number of columns in grid layout."""
        return 3

    def spacing(self) -> int:
        """Spacing between items."""
        return 3

    def item_width(self) -> int:
        """Width of each command item."""
        return 100  # Adjust based on font and expected text length

    def item_height(self) -> int:
        """Height of each item."""
        return 36

    def window_width(self) -> int:
        """Default window width: fits col_max items with spacing."""
        return (self.item_width() + self.spacing()) * self.col_max - self.spacing()

    def window_height(self) -> int:
        """Fixed height for one row."""
        return self.item_height()

    def contents_width(self) -> int:
        """Total width of all items (may exceed window width)."""
        count = self.item_max
        return (self.item_width() + self.spacing()) * count - self.spacing() if count > 0 else 1

    def contents_height(self) -> int:
        """Contents height is just one item high."""
        return self.item_height()

    # -------------------------------------------------------------------------
    # Scrolling & Column Management

    def top_col(self) -> int:
        """Index of the leftmost visible column."""
        return self.ox // (self.item_width() + self.spacing())

    def set_top_col(self, col: int):
        """Set the leftmost visible column with clamping."""
        max_top = max(0, self.item_max - self.col_max)  # Prevent over-scroll
        clamped = max(0, min(col, max_top))
        self.ox = clamped * (self.item_width() + self.spacing())

    def bottom_col(self) -> int:
        """Index of the rightmost visible column."""
        return self.top_col() + self.col_max - 1

    def set_bottom_col(self, col: int):
        """Set the rightmost visible column by adjusting top_col."""
        self.set_top_col(col - (self.col_max - 1))

    def ensure_cursor_visible(self):
        """Scroll so that the current selection is visible."""
        if self.index < self.top_col():
            self.set_top_col(self.index)
        elif self.index > self.bottom_col():
            self.set_bottom_col(self.index)

    # -------------------------------------------------------------------------
    # Item Geometry

    def item_rect(self, index: int) -> Rect:
        """
        Get screen-space rectangle for item at given index.
        Position accounts for horizontal scroll (ox).
        """
        # item_width = self.contents_width // self.col_max
        # x = self.x + self.padding + index * item_width
        # y = self.y + self.padding
        # return (x, y, item_width, self.line_height)
    
        x = index * (self.item_width() + self.spacing()) - (self.ox or 0)
        y = 0
        return Rect(x, y, self.item_width(), self.item_height())

    def item_rect_for_text(self, index: int) -> Rect:
        """Get inner rectangle for drawing text (with padding)."""
        rect = self.item_rect(index)
        padding = 4
        return Rect(
            rect.x + padding,
            rect.y + (rect.height - 24) // 2,  # Vertically center (assuming ~24px font)
            rect.width - padding * 2,
            24
        )

    # -------------------------------------------------------------------------
    # Appearance & Interaction

    def alignment(self) -> int:
        """Text alignment: 1 = center."""
        return 1

    def draw_item(self, index: int):
        """Draw a single command item."""
        item = self._list[index]
        rect = self.item_rect_for_text(index)

        # Choose color based on enabled state
        color = C_BLACK if item['enabled'] else C_DARK

        # Center text horizontally
        text = item['name']
        char_width = 8  # Approximate monospace width; replace with real measure if available
        text_width = len(text) * char_width
        text_x = rect.x + (rect.width - text_width) // 2
        text_y = rect.y

        dtext(text_x, text_y, color, text)

    # -------------------------------------------------------------------------
    # Input Handling (Disabled Vertical Navigation)

    def cursor_down(self, wrap: bool = False):
        """Disabled: no vertical movement."""
        pass

    def cursor_up(self, wrap: bool = False):
        """Disabled: no vertical movement."""
        pass

    def cursor_pagedown(self):
        """Disabled."""
        pass

    def cursor_pageup(self):
        """Disabled."""
        pass

    # -------------------------------------------------------------------------
    # Refresh & Update

    def refresh(self):
        """Rebuild content and ensure selection is visible."""
        super().refresh()
        self.ensure_cursor_visible()

    def update(self):
        """Override update if needed; ensure scroll stays valid."""
        super().update()
        self.ensure_cursor_visible()