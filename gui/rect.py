# gui/rect.py

class Point:
    """Represents a 2D coordinate."""
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return isinstance(other, Point) and self.x == other.x and self.y == other.y

    def copy(self):
        return Point(self.x, self.y)

class Rect:
    """
    Represents a rectangle with integer coordinates.
    Provides properties and methods for manipulation and inspection.
    """
    def __init__(self, left=0, top=0, right=0, bottom=0):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

    @property
    def width(self):
        """The width of the rectangle."""
        return self.right - self.left + 1

    @property
    def height(self):
        """The height of the rectangle."""
        return self.bottom - self.top + 1

    @property
    def center(self):
        """The center Point of the rectangle."""
        cx = self.left + (self.width // 2)
        cy = self.top + (self.height // 2)
        return Point(cx, cy)
    
    @property
    def top_left(self):
        """The top-left Point of the rectangle."""
        return Point(self.left, self.top)

    def contains(self, x, y=None):
        """Checks if a Point or (x, y) coordinate is inside the rectangle."""
        if isinstance(x, Point):
            px, py = x.x, x.y
        elif y is not None:
            px, py = x, y
        else:
            raise TypeError("contains() requires a Point or two integers.")
            
        return self.left <= px <= self.right and self.top <= py <= self.bottom

    def overlaps(self, other):
        """Checks if this rectangle overlaps with another."""
        return not (other.left > self.right or other.right < self.left or
                    other.top > self.bottom or other.bottom < self.top)

    def move_to(self, x, y):
        """Moves the rectangle to a new top-left position without changing its size."""
        w, h = self.width, self.height
        self.left = x
        self.top = y
        self.right = x + w - 1
        self.bottom = y + h - 1

    def shift(self, dx, dy):
        """Moves the rectangle by a given delta."""
        self.left += dx
        self.top += dy
        self.right += dx
        self.bottom += dy

    def copy(self):
        """Returns a new Rect with the same dimensions."""
        return Rect(self.left, self.top, self.right, self.bottom)

    def __repr__(self):
        return f"Rect(left={self.left}, top={self.top}, width={self.width}, height={self.height})"