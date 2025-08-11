# gui/layouts.py
from .base import Widget
from .rect import Rect

class LinearLayout(Widget):
    """Arranges children in a single horizontal or vertical line."""
    VERTICAL = 0
    HORIZONTAL = 1

    def __init__(self, x, y, width, height, orientation=VERTICAL, padding=2):
        super().__init__(x, y, width, height)
        self.orientation = orientation
        self.padding = padding

    def add_child(self, child):
        """Adds a child and repositions all children."""
        super().add_child(child)
        self.do_layout()

    def do_layout(self):
        """Positions children according to the orientation."""
        x_offset = self.padding
        y_offset = self.padding
        
        for child in self.children:
            if not child.visible:
                continue

            if self.orientation == self.VERTICAL:
                child.rect.move_to(x_offset, y_offset)
                y_offset += child.rect.height + self.padding
            else: # HORIZONTAL
                child.rect.move_to(x_offset, y_offset)
                x_offset += child.rect.width + self.padding
        
        self.set_needs_redraw()

class FrameLayout(Widget):
    """Stacks children on top of each other, aligned to the top-left."""
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)

    def add_child(self, child):
        """Adds a child and ensures it's positioned at the top-left."""
        super().add_child(child)
        child.rect.move_to(0, 0)
        child.rect.right = self.rect.width - 1
        child.rect.bottom = self.rect.height - 1

    def show_child(self, child_to_show):
        """Makes one child visible and hides all others."""
        if child_to_show not in self.children:
            self.add_child(child_to_show)

        for child in self.children:
            child.visible = (child == child_to_show)
        
        self.set_needs_redraw()
