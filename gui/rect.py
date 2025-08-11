# gui/rect.py
try:
    from typing import Optional, Tuple
except ImportError:
    pass

class Point:
    """Represents a 2D coordinate."""
    def __init__(self, x: int = 0, y: int = 0):
        self.x = x
        self.y = y

    def __eq__(self, other) -> bool:
        return isinstance(other, Point) and self.x == other.x and self.y == other.y

    def copy(self) -> 'Point':
        return Point(self.x, self.y)

class Rect:
    """
    Represents a rectangle with integer coordinates.
    Provides properties and methods for manipulation and inspection.
    """
    def __init__(self, left: int = 0, top: int = 0, right: int = 0, bottom: int = 0):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

    @property
    def width(self) -> int:
        """The width of the rectangle."""
        return self.right - self.left + 1

    @property
    def height(self) -> int:
        """The height of the rectangle."""
        return self.bottom - self.top + 1

    @property
    def center(self) -> Point:
        """The center Point of the rectangle."""
        cx = self.left + (self.width // 2)
        cy = self.top + (self.height // 2)
        return Point(cx, cy)
    
    @property
    def top_left(self) -> Point:
        """The top-left Point of the rectangle."""
        return Point(self.left, self.top)

    def contains(self, x: int, y: Optional[int] = None) -> bool:
        """Checks if a Point or (x, y) coordinate is inside the rectangle."""
        if isinstance(x, Point):
            px, py = x.x, x.y
        elif y is not None:
            px, py = x, y
        else:
            # This path is for when a Point object is passed as the first argument.
            # We assume it's a Point and proceed. A TypeError would occur on attribute access if not.
            px, py = x.x, x.y
            
        return self.left <= px <= self.right and self.top <= py <= self.bottom

    def overlaps(self, other: 'Rect') -> bool:
        """Checks if this rectangle overlaps with another."""
        return not (other.left > self.right or other.right < self.left or
                    other.top > self.bottom or other.bottom < self.top)

    def move_to(self, x: int, y: int) -> None:
        """Moves the rectangle to a new top-left position without changing its size."""
        w, h = self.width, self.height
        self.left = x
        self.top = y
        self.right = x + w - 1
        self.bottom = y + h - 1

    def shift(self, dx: int, dy: int) -> None:
        """Moves the rectangle by a given delta."""
        self.left += dx
        self.top += dy
        self.right += dx
        self.bottom += dy

    def copy(self) -> 'Rect':
        """Returns a new Rect with the same dimensions."""
        return Rect(self.left, self.top, self.right, self.bottom)

    def __repr__(self) -> str:
        return f"Rect(left={self.left}, top={self.top}, width={self.width}, height={self.height})"