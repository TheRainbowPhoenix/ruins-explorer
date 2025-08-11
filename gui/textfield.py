import gint
from .base import Widget, GUIEvent

class TextField(Widget):
    """A single-line text input field."""
    def __init__(self, x: int, y: int, width: int, initial_text: str = ""):
        # A text field has a fixed height.
        height = 18
        super().__init__(x, y, width, height)
        self.text = initial_text
        self.cursor_pos = len(initial_text)
        self.is_focused = False
        self.cursor_visible = False

    def on_focus_gained(self) -> None:
        """Called by the application when this widget gets focus."""
        self.is_focused = True
        self.cursor_visible = True
        self.set_needs_redraw()

    def on_focus_lost(self) -> None:
        """Called by the application when this widget loses focus."""
        self.is_focused = False
        self.cursor_visible = False
        self.set_needs_redraw()

    def on_event(self, event: GUIEvent) -> bool:
        if not self.is_focused or event.type != "key_press":
            return False

        # Handle backspace
        if event.key == gint.KEY_DEL:
            if self.cursor_pos > 0:
                self.text = self.text[:self.cursor_pos - 1] + self.text[self.cursor_pos:]
                self.cursor_pos -= 1
                self.set_needs_redraw()
        
        # This is a very simplified character map for demonstration.
        # A real application would need a more comprehensive mapping.
        key_map = {
            gint.KEY_0: '0', gint.KEY_1: '1', gint.KEY_2: '2', gint.KEY_3: '3',
            gint.KEY_4: '4', gint.KEY_5: '5', gint.KEY_6: '6', gint.KEY_7: '7',
            gint.KEY_8: '8', gint.KEY_9: '9', gint.KEY_DOT: '.',
        }
        
        char = key_map.get(event.key)
        if char:
            self.text = self.text[:self.cursor_pos] + char + self.text[self.cursor_pos:]
            self.cursor_pos += 1
            self.set_needs_redraw()
            
        return True # Consume the key press

    def on_draw(self) -> None:
        abs_rect = self.get_absolute_rect()
        
        # Draw border and background
        bg_color = gint.C_WHITE
        border_color = gint.C_BLUE if self.is_focused else gint.C_BLACK
        gint.drect(abs_rect.left, abs_rect.top, abs_rect.right, abs_rect.bottom, bg_color)
        gint.drect_border(abs_rect.left, abs_rect.top, abs_rect.right, abs_rect.bottom, 
                          gint.C_NONE, 1, border_color)
        
        # Draw the text content
        gint.dtext(abs_rect.left + 3, abs_rect.top + 3, gint.C_BLACK, self.text)
        
        # Draw the blinking cursor
        if self.cursor_visible:
            cursor_x = abs_rect.left + 3 + (self.cursor_pos * 8)
            gint.dline(cursor_x, abs_rect.top + 2, cursor_x, abs_rect.bottom - 2, gint.C_BLACK)
