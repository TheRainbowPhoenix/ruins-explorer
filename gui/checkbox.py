import gint
from .base import Widget, GUIEvent

try:
    from typing import Optional, Any
except ImportError:
    pass

class Checkbox(Widget):
    """A simple two-state checkbox widget."""
    def __init__(self, x: int = 0, y: int = 0, is_checked: bool = False, event_id: Optional[Any] = None):
        # A checkbox is a fixed size, e.g., 16x16 pixels.
        super().__init__(x, y, 16, 16)
        self.is_checked = is_checked
        self.event_id = event_id

    def on_event(self, event: GUIEvent) -> bool:
        if event.type == "touch_up" and event.source is self:
            self.is_checked = not self.is_checked
            self.set_needs_redraw()
            
            # Fire a state changed event for the application to handle.
            state_event = GUIEvent(
                "state_changed", self, 
                checkbox_id=self.event_id, 
                is_checked=self.is_checked
            )
            ancestor = self
            while ancestor.parent:
                ancestor = ancestor.parent
            ancestor.handle_event(state_event)
            
            return True
        return False

    def on_draw(self) -> None:
        abs_rect = self.get_absolute_rect()
        
        # Draw the outer box
        gint.drect_border(abs_rect.left, abs_rect.top, abs_rect.right, abs_rect.bottom,
                          gint.C_WHITE, 1, gint.C_BLACK)
        
        # Draw the checkmark if checked
        if self.is_checked:
            # Draw a simple 'X' as the checkmark
            gint.dline(abs_rect.left + 3, abs_rect.top + 3, abs_rect.right - 3, abs_rect.bottom - 3, gint.C_BLACK)
            gint.dline(abs_rect.left + 3, abs_rect.bottom - 3, abs_rect.right - 3, abs_rect.top + 3, gint.C_BLACK)
