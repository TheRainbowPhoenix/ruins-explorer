# Contains basic, integer-based data structures for position and collision.
import math
try:
    from typing import Union, Optional, Tuple, Any
except ImportError:
    pass

class Vec2:
    """Vector2 when you don't want the noise."""
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
    def __add__(self, other: 'Vec2') -> 'Vec2':
        return Vec2(self.x + other.x, self.y + other.y)
    def __mul__(self, scalar: int) -> 'Vec2':
        return Vec2(self.x * scalar, self.y * scalar)

class Vector2:
    """A 2D vector using integers, suitable for fixed-point math."""
    
    # Static constants
    ZERO: Optional['Vector2'] = None
    ONE: Optional['Vector2'] = None
    UP: Optional['Vector2'] = None
    DOWN: Optional['Vector2'] = None
    LEFT: Optional['Vector2'] = None
    RIGHT: Optional['Vector2'] = None
    
    def __init__(self, x: Union[int, 'Vector2', dict, None] = 0, y: Optional[int] = None):
        if isinstance(x, Vector2):
            self.x = x.x
            self.y = x.y
        elif isinstance(x, dict) and 'x' in x and 'y' in x:
            self.x = int(x['x'])
            self.y = int(x['y'])
        elif x is None:
            self.x = 0
            self.y = 0
        else:
            self.x = int(x) # type: ignore
            self.y = int(y) if y is not None else int(x) # type: ignore
    
    def __add__(self, other: 'Vector2') -> 'Vector2':
        return Vector2(self.x + other.x, self.y + other.y)
    
    def __mul__(self, scalar: int) -> 'Vector2':
        return Vector2(self.x * scalar, self.y * scalar)
    
    def __repr__(self) -> str:
        return f"Vector2({self.x}, {self.y})"
    
    def add(self, src: 'Vector2') -> 'Vector2':
        """Add a given Vector to this Vector."""
        self.x += src.x
        self.y += src.y
        return self
    
    def angle(self) -> float:
        """Calculate the angle between this Vector and the positive x-axis, in radians."""
        return math.atan2(self.y, self.x)
    
    def clone(self) -> 'Vector2':
        """Make a clone of this Vector2."""
        return Vector2(self.x, self.y)
    
    def copy(self, src: 'Vector2') -> 'Vector2':
        """Copy the components of a given Vector into this Vector."""
        self.x = src.x
        self.y = src.y
        return self
    
    def cross(self, src: 'Vector2') -> int:
        """Calculate the cross product of this Vector and the given Vector."""
        return self.x * src.y - self.y * src.x
    
    def distance(self, src: 'Vector2') -> float:
        """Calculate the distance between this Vector and the given Vector."""
        return math.sqrt(self.distance_sq(src))
    
    def distance_sq(self, src: 'Vector2') -> int:
        """Calculate the distance between this Vector and the given Vector, squared."""
        dx = self.x - src.x
        dy = self.y - src.y
        return dx * dx + dy * dy
    
    def divide(self, src: 'Vector2') -> 'Vector2':
        """Perform a component-wise division between this Vector and the given Vector."""
        self.x = int(self.x / src.x) if src.x != 0 else 0
        self.y = int(self.y / src.y) if src.y != 0 else 0
        return self
    
    def dot(self, src: 'Vector2') -> int:
        """Calculate the dot product of this Vector and the given Vector."""
        return self.x * src.x + self.y * src.y
    
    def equals(self, v: 'Vector2') -> bool:
        """Check whether this Vector is equal to a given Vector."""
        return self.x == v.x and self.y == v.y
    
    def fuzzy_equals(self, v: 'Vector2', epsilon: float = 0.0001) -> bool:
        """Check whether this Vector is approximately equal to a given Vector."""
        return abs(self.x - v.x) < epsilon and abs(self.y - v.y) < epsilon
    
    def length(self) -> float:
        """Calculate the length (or magnitude) of this Vector."""
        return math.sqrt(self.x * self.x + self.y * self.y)
    
    def length_sq(self) -> int:
        """Calculate the length of this Vector squared."""
        return self.x * self.x + self.y * self.y
    
    def lerp(self, src: 'Vector2', t: float = 0) -> 'Vector2':
        """Linearly interpolate between this Vector and the given Vector."""
        self.x = int(self.x + (src.x - self.x) * t)
        self.y = int(self.y + (src.y - self.y) * t)
        return self
    
    def limit(self, max_val: float) -> 'Vector2':
        """Limit the length (or magnitude) of this Vector."""
        length_sq = self.length_sq()
        if length_sq > max_val * max_val:
            length = math.sqrt(length_sq)
            self.x = int(self.x * max_val / length)
            self.y = int(self.y * max_val / length)
        return self
    
    def mirror(self, axis: 'Vector2') -> 'Vector2':
        """Reflect this Vector across another."""
        dot = self.dot(axis) * 2
        self.x = int(self.x - axis.x * dot)
        self.y = int(self.y - axis.y * dot)
        return self
    
    def multiply(self, src: 'Vector2') -> 'Vector2':
        """Perform a component-wise multiplication between this Vector and the given Vector."""
        self.x *= src.x
        self.y *= src.y
        return self
    
    def negate(self) -> 'Vector2':
        """Negate the x and y components of this Vector."""
        self.x = -self.x
        self.y = -self.y
        return self
    
    def normalize(self) -> 'Vector2':
        """Normalize this Vector."""
        length = self.length()
        if length > 0:
            self.x = int(self.x / length)
            self.y = int(self.y / length)
        return self
    
    def normalize_left_hand(self) -> 'Vector2':
        """Rotate this Vector to its perpendicular, in the negative direction."""
        x = self.x
        self.x = self.y
        self.y = -x
        return self
    
    def normalize_right_hand(self) -> 'Vector2':
        """Rotate this Vector to its perpendicular, in the positive direction."""
        x = self.x
        self.x = -self.y
        self.y = x
        return self
    
    def reflect(self, normal: 'Vector2') -> 'Vector2':
        """Reflect this Vector off a line defined by a normal."""
        dot = self.dot(normal) * 2
        self.x = int(self.x - normal.x * dot)
        self.y = int(self.y - normal.y * dot)
        return self
    
    def reset(self) -> 'Vector2':
        """Make this Vector the zero vector (0, 0)."""
        self.x = 0
        self.y = 0
        return self
    
    def rotate(self, delta: float) -> 'Vector2':
        """Rotate this Vector by an angle amount."""
        cos = math.cos(delta)
        sin = math.sin(delta)
        x = self.x * cos - self.y * sin
        y = self.x * sin + self.y * cos
        self.x = int(x)
        self.y = int(y)
        return self
    
    def scale(self, value: int) -> 'Vector2':
        """Scale this Vector by the given value."""
        self.x *= value
        self.y *= value
        return self
    
    def set(self, x: Union[int, 'Vector2', dict], y: Optional[int] = None) -> 'Vector2':
        """Set the x and y components of this Vector."""
        if isinstance(x, Vector2):
            self.x = x.x
            self.y = x.y
        elif isinstance(x, dict) and 'x' in x and 'y' in x:
            self.x = int(x['x'])
            self.y = int(x['y'])
        else:
            self.x = int(x) # type: ignore
            self.y = int(y) if y is not None else int(x) # type: ignore
        return self
    
    def set_angle(self, angle: float) -> 'Vector2':
        """Set the angle of this Vector."""
        length = self.length()
        self.x = int(math.cos(angle) * length)
        self.y = int(math.sin(angle) * length)
        return self
    
    def set_from_object(self, obj: Any) -> 'Vector2':
        """Set the component values of this Vector from a given Vector2Like object."""
        if hasattr(obj, 'x') and hasattr(obj, 'y'):
            self.x = int(obj.x)
            self.y = int(obj.y)
        return self
    
    def set_length(self, length: float) -> 'Vector2':
        """Set the length (or magnitude) of this Vector."""
        current_length = self.length()
        if current_length > 0:
            self.scale(int(length / current_length))
        return self
    
    def set_to(self, x: Union[int, 'Vector2', dict], y: Optional[int] = None) -> 'Vector2':
        """Alias for set method."""
        return self.set(x, y)
    
    def set_to_polar(self, azimuth: float, radius: float = 1) -> 'Vector2':
        """Sets the x and y values of this object from a given polar coordinate."""
        self.x = int(math.cos(azimuth) * radius)
        self.y = int(math.sin(azimuth) * radius)
        return self
    
    def subtract(self, src: 'Vector2') -> 'Vector2':
        """Subtract the given Vector from this Vector."""
        self.x -= src.x
        self.y -= src.y
        return self

Vector2.ZERO = Vector2(0, 0)
Vector2.ONE = Vector2(1, 1)
Vector2.UP = Vector2(0, -1)
Vector2.DOWN = Vector2(0, 1)
Vector2.LEFT = Vector2(-1, 0)
Vector2.RIGHT = Vector2(1, 0)

class Point:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

class Rect:
    """An integer-based rectangle defined by a position, width, and height."""
    def __init__(self, x: int, y: int, w: int, h: int):
        self.x, self.y, self.w, self.h = x, y, w, h
    
    @property
    def left(self) -> int:
        return self.x

    @property
    def right(self) -> int:
        return self.x + self.w

    @property
    def top(self) -> int:
        return self.y

    @property
    def bottom(self) -> int:
        return self.y + self.h

    def intersects(self, other: 'Rect') -> bool:
        return self.right > other.left and self.left < other.right and \
               self.bottom > other.top and self.top < other.bottom

    @property
    def width(self) -> int:
        return self.w

    @property
    def height(self) -> int:
        return self.h

    @property
    def size(self) -> Tuple[int, int]:
        return (self.w, self.h)

    @property
    def center(self) -> Point:
        cx = self.x + (self.w // 2)
        cy = self.y + (self.h // 2)
        return Point(cx, cy)

    @property
    def top_left(self) -> Point:
        return Point(self.x, self.y)

    def contains(self, x: int, y: Optional[int] = None) -> bool:
        if isinstance(x, Point):
            px, py = x.x, x.y
        elif y is not None:
            px, py = x, y
        else:
            raise ValueError("Invalid arguments to contains()")
        return self.x <= px < self.x + self.w and self.y <= py < self.y + self.h

    def overlaps(self, other: 'Rect') -> bool:
        return not (other.x >= self.x + self.w or
                    other.x + other.w <= self.x or
                    other.y >= self.y + self.h or
                    other.y + other.h <= self.y)

    def move_to(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def shift(self, dx: int, dy: int) -> None:
        self.x += dx
        self.y += dy

    def copy(self) -> 'Rect':
        return Rect(self.x, self.y, self.w, self.h)

    def intersect(self, other: 'Rect') -> 'Rect':
        left = max(self.x, other.x)
        top = max(self.y, other.y)
        right = min(self.x + self.w, other.x + other.w)
        bottom = min(self.y + self.h, other.y + other.h)
        if left < right and top < bottom:
            return Rect(left, top, right - left, bottom - top)
        else:
            return Rect(0, 0, 0, 0)  # Empty rectangle

    def union(self, other: 'Rect') -> 'Rect':
        if self.w == 0 or self.h == 0:
            return other.copy()
        if other.w == 0 or other.h == 0:
            return self.copy()
        left = min(self.x, other.x)
        top = min(self.y, other.y)
        right = max(self.x + self.w, other.x + other.w)
        bottom = max(self.y + self.h, other.y + other.h)
        return Rect(left, top, right - left, bottom - top)