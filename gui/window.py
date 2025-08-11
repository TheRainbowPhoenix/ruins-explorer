# gui/window.py
import gint
from .base import Widget
from .layouts import LinearLayout

class Window(Widget):
    """A floating window that appears on top of other content."""
    def __init__(self, x, y, width, height, title=""):
        super().__init__(x, y, width, height)
        self.title = title
        # Make this window a top-level element by default
        self.parent = None 
        
        # A simple layout for content
        self.content = LinearLayout(1, 12, width - 2, height - 13, orientation=LinearLayout.VERTICAL, padding=2)
        self.add_child(self.content)

    def on_draw(self):
        abs_rect = self.get_absolute_rect()
        
        # Draw frame
        gint.drect(abs_rect.left, abs_rect.top, abs_rect.right, abs_rect.bottom, gint.C_WHITE)
        gint.drect_border(abs_rect.left, abs_rect.top, abs_rect.right, abs_rect.bottom, 
                          gint.C_NONE, 1, gint.C_BLACK)

        # Draw title bar
        gint.drect(abs_rect.left + 1, abs_rect.top + 1, abs_rect.right - 1, abs_rect.top + 11, gint.C_BLUE)
        gint.dtext(abs_rect.left + 3, abs_rect.top + 2, gint.C_WHITE, self.title)

    def add_widget(self, widget):
        self.content.add_child(widget)
