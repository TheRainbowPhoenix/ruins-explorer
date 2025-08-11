import gint
from .base import Widget
from .layouts import LinearLayout

class Toolbar(LinearLayout):
    """A container for buttons, typically at the top of an application."""
    def __init__(self, x, y, width, height=30):
        super().__init__(x, y, width, height, orientation=LinearLayout.HORIZONTAL, padding=3)

    def on_draw(self):
        abs_rect = self.get_absolute_rect()
        # TODO: Draw a textured background for the toolbar
        gint.drect(abs_rect.left, abs_rect.top, abs_rect.right, abs_rect.bottom, gint.C_RGB(25, 25, 25)) # Dark grey

