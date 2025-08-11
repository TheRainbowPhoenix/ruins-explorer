# gui/layouts.py
from .base import Widget
from .rect import Rect

class WrappingLayout(Widget):
    """Arranges children in a line and resizes itself to wrap them."""
    VERTICAL = 0
    HORIZONTAL = 1

    def __init__(self, x: int, y: int, orientation: int = VERTICAL, padding: int = 2):
        super().__init__(x, y, 0, 0)
        self.orientation = orientation
        self.padding = padding

    def add_child(self, child: Widget) -> None:
        super().add_child(child)
        self.do_layout()

    def do_layout(self) -> None:
        x_offset, y_offset = self.padding, self.padding
        max_x, max_y = 0, 0
        
        for child in self.children:
            if not child.visible: continue
            child.rect.move_to(x_offset, y_offset)
            if self.orientation == self.VERTICAL:
                y_offset += child.rect.height + self.padding
                if child.rect.width > max_x: max_x = child.rect.width
            else:
                x_offset += child.rect.width + self.padding
                if child.rect.height > max_y: max_y = child.rect.height

        if self.orientation == self.VERTICAL:
            self.rect.right = self.rect.left + max_x + self.padding * 2 - 1
            self.rect.bottom = self.rect.top + y_offset - 1
        else:
            self.rect.right = self.rect.left + x_offset - 1
            self.rect.bottom = self.rect.top + max_y + self.padding * 2 - 1
        self.set_needs_redraw()

class LinearLayout(Widget):
    """Arranges children in a single horizontal or vertical line."""
    VERTICAL = 0
    HORIZONTAL = 1

    def __init__(self, x: int, y: int, width: int, height: int, orientation: int = VERTICAL, padding: int = 2):
        super().__init__(x, y, width, height)
        self.orientation = orientation
        self.padding = padding

    def add_child(self, child: Widget) -> None:
        super().add_child(child)
        self.do_layout()

    def do_layout(self) -> None:
        x_offset, y_offset = self.padding, self.padding
        for child in self.children:
            if not child.visible: continue
            child.rect.move_to(x_offset, y_offset)
            if self.orientation == self.VERTICAL:
                y_offset += child.rect.height + self.padding
            else:
                x_offset += child.rect.width + self.padding
        self.set_needs_redraw()

class VBox(WrappingLayout):
    """A vertical layout that wraps its content."""
    def __init__(self, x: int = 0, y: int = 0, padding: int = 2):
        super().__init__(x, y, orientation=WrappingLayout.VERTICAL, padding=padding)

class HBox(WrappingLayout):
    """A horizontal layout that wraps its content."""
    def __init__(self, x: int = 0, y: int = 0, padding: int = 2):
        super().__init__(x, y, orientation=WrappingLayout.HORIZONTAL, padding=padding)

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
