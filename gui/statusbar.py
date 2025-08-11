# gui/statusbar.py
from .base import Widget
from .label import Label
import gint

C_LIGHT = 0xD69A


class StatusBar(Widget):
    """A bar at the bottom of the application to display status messages."""
    def __init__(self, x, y, width, height=14):
        super().__init__(x, y, width, height)
        self.label = Label(2, 1, "Ready")
        self.add_child(self.label)

    def set_text(self, text):
        self.label.set_text(text)

    def on_draw(self):
        abs_rect = self.get_absolute_rect()
        # TODO: Draw a textured background for the status bar
        gint.drect(abs_rect.left, abs_rect.top, abs_rect.right, abs_rect.bottom, C_LIGHT)