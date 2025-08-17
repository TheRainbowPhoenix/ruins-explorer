- `__init__.py`
```

```

- `engine\__init__.py`
```

```

- `engine\animation.py`
```
# engine/animation.py
# Manages animation frames and state.
try:
    from typing import Optional, List
except:
    pass

class AnimationFrame:
    """Represents a single frame of an animation, loaded from asset data."""
    def __init__(self, img, imgH, x, y, w, h, cx, cy, duration):
        self.img, self.imgH = img, imgH
        self.x, self.y, self.w, self.h = x, y, w, h
        self.cx, self.cy = cx, cy
        self.duration = duration

class AnimationState:
    """Manages the state of an active animation for a game object."""
    def __init__(self):
        self.frames: Optional[List[AnimationFrame]] = None
        self.index: int = -1
        self.elapsed: float = 0.0

    def set(self, frames: List[AnimationFrame]):
        """Sets a new animation and resets its state."""
        self.frames, self.index, self.elapsed = frames, 0, 0.0

    def update(self, dt: float) -> bool:
        """
        Advances the animation by a time delta.
        Returns True if the animation has just looped.
        """
        if self.index < 0 or not self.frames: return False
        self.elapsed += dt
        if self.elapsed * 1000 >= self.frames[self.index].duration:
            self.elapsed = 0
            self.index = (self.index + 1) % len(self.frames)
            return self.index == 0
        return False

    def get_current_frame(self) -> Optional[AnimationFrame]:
        """Returns the current frame of the animation."""
        if self.frames and self.index >= 0:
            return self.frames[self.index]
        return None

    def is_animation_finished(self) -> bool:
        """Checks if the animation has completed a full cycle."""
        return self.index == len(self.frames) - 1 if self.frames else False

```

- `engine\assets.py`
```
# engine/asset.py
# A central manager to load and process all game data.

from cpgame.engine.animation import AnimationFrame
from cpgame.game_assets import templar_data
from cpgame.game_assets import jrpg_data
from cpgame.game_assets.fanta_tiles import image as fanta_tileset_img # Your raw JRPG tileset image

try:
    from typing import Optional, List, Dict
except:
    pass

class Tilemap:
    def __init__(self, img, tileboxes, solid_ids):
        self.img = img
        self.tileboxes = tileboxes
        self.solid = solid_ids

class AssetManager:
    """
    A singleton class that loads all assets once at the start of the game.
    This mimics Phaser's loader, but pre-loads everything for simplicity.
    """
    def __init__(self):
        self.animations: Dict[str, List[AnimationFrame]] = {}
        self.tilesets: Dict[str, Tilemap] = {} # tilemap
        self.maps: Dict[str, Dict] = {}
        self.is_loaded = False

    def load_all(self):
        """Processes all raw asset data into usable game objects."""
        if self.is_loaded: return
        print("AssetManager: Loading all assets...")

        # TODO: use PAK if successful, and make it a PAK loader
        # TODO: else, use the class loader with cleanup

        # --- Load Templar Assets ---
        for name, data in templar_data.sprites.items(): # type: ignore
            self.animations[name] = [AnimationFrame(*frame) for frame in data]
        for name, data in templar_data.bounce.items(): # type: ignore
            self.animations[name] = [AnimationFrame(*frame) for frame in data]
        self.tilesets["templar"] = Tilemap(*templar_data.tileset) # type: ignore

        # --- Load JRPG Assets ---
        self.tilesets["jrpg"] = Tilemap(fanta_tileset_img, [], jrpg_data.solid_tiles) # type: ignore
        self.maps["jrpg_village"] = {
            "layout": jrpg_data.map_layout, # type: ignore
            "objects": jrpg_data.map_objects, # type: ignore
            "signs": jrpg_data.map_signs # type: ignore
        }
        
        self.is_loaded = True
        print("AssetManager: Load complete.")
```

- `engine\game.py`
```
# engine/game.py
# The main game class with the fixed-timestep loop and scene management.

import time
from gint import *
from cpgame.engine.scene import Scene
from cpgame.engine.assets import AssetManager
from cpgame.game_scenes.menu_scene import MenuScene # TODO: should be dynamic ?

try:
    from typing import Optional, List
except:
    pass

DEBUG_FRAME_TIME = False

class Game:
    """The main Game class, equivalent to Phaser.Game."""
    def __init__(self):
        self.scenes: List[Scene] = []
        self.assets = AssetManager()
        self.running: bool = False
        self.fixed_timestep: float = 0.055
        self.frame_cap_ms: int = 53

    def start(self, initial_scene_class):
        """Initializes assets and starts the game with the first scene."""
        self.assets.load_all()
        self.running = True
        self.change_scene(initial_scene_class)

        while self.running and self.scenes:
            frame_start_time = time.ticks_ms()
            current_scene = self.scenes[-1]

            # --- LOGIC UPDATE ---
            signal = current_scene.update(self.fixed_timestep)
            if signal == "EXIT_GAME": self.running = False; break

            # --- RENDER ---
            render_start_time = time.ticks_ms()
            current_scene.draw(time.ticks_diff(time.ticks_ms(), render_start_time))
            dupdate()

            # --- FRAME CAP ---
            frame_time_ms = time.ticks_diff(time.ticks_ms(), frame_start_time)
            if DEBUG_FRAME_TIME: print(f"Frame Time: {frame_time_ms}ms")
            if frame_time_ms < self.frame_cap_ms:
                time.sleep_ms(self.frame_cap_ms - frame_time_ms)
    
    def change_scene(self, new_scene_class):
        """Stops the current scene and starts a new one."""
        if self.scenes:
            self.scenes[-1].destroy()
            self.scenes.pop()
        
        new_scene = new_scene_class(self)
        self.scenes.append(new_scene)
        new_scene.create()
```

- `engine\geometry.py`
```
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
```

- `engine\scene.py`
```
# engine/scene.py
# Defines the core Scene class and the SceneManager.

from cpgame.engine.systems import InputManager, Camera
from cpgame.engine.assets import AssetManager
try:
    from typing import Optional, List
    from cpgame.engine.game import Game
except:
    pass

class Scene:
    """
    The base class for all game states, inspired by Phaser.Scene.
    A Scene has a lifecycle: init -> create -> update/draw -> destroy.
    """
    def __init__(self, game: 'Game'):
        self.game = game
        # Each scene gets its own instances of engine systems.
        self.input = InputManager()
        self.camera = Camera()
        self.assets = game.assets

    def create(self):
        """Called once when the scene is started."""
        pass

    def update(self, dt: float) -> Optional[str]:
        """
        Called every logic frame. 'dt' is the fixed timestep.
        Can return a string signal like "CHANGE_SCENE" to the game loop.
        """
        pass

    def draw(self, frame_time_ms: int):
        """Called every render frame to draw the scene."""
        pass

    def destroy(self):
        """Called when the scene is being shut down, for cleanup."""
        pass

```

- `engine\systems.py`
```
# Contains helper systems like Input and Camera.

from gint import keydown, keypressed, cleareventflips, clearevents
from gint import KEY_RIGHT, KEY_LEFT, KEY_DOWN, KEY_UP, KEY_EXE, KEY_MENU, KEY_EXIT, KEY_SHIFT

class InputManager:
    """
    A class to poll and hold a snapshot of the input state for a single frame.
    Mimics the concept of `this.input` in Phaser.
    """
    def __init__(self):
        self.dx: int = 0
        self.dy: int = 0

        self.up: bool = False
        self.down: bool = False
        self.left: bool = False
        self.right: bool = False
        self.interact: bool = False
        self.menu: bool = False
        self.exit: bool = False
        self.shift: bool = False

        # TODO: 8Dir with numpad ? 5 = OK
        # TODO: define a custom mapping ?

    def update(self):
        """Polls the hardware. This should be called once per logic update."""
        cleareventflips()
        clearevents()
        # Poll continuous state (`keydown`)
        self.dx = keydown(KEY_RIGHT) - keydown(KEY_LEFT)
        self.dy = keydown(KEY_DOWN) - keydown(KEY_UP)
        
        # Poll one-shot press state (`keypressed`)
        self.up = keypressed(KEY_UP)
        self.down = keypressed(KEY_DOWN)
        self.left = keypressed(KEY_LEFT)
        self.right = keypressed(KEY_RIGHT)
        self.interact = keypressed(KEY_EXE)
        self.menu = keypressed(KEY_MENU)
        self.exit = keypressed(KEY_EXIT)
        self.shift = keypressed(KEY_SHIFT)

class Camera:
    """A basic camera that can be used by scenes."""
    def __init__(self, x: int = 0, y: int = 0):
        self.x = x
        self.y = y

```

- `game_assets\__init__.py`
```

```

- `game_assets\fanta_tiles.py`
```
"" 

```

- `game_assets\jrpg_data.py`
```
# assets/jrpg_data.py
# Data for the JRPG scene, including a static map.

# Tile IDs that the player cannot walk on.
solid_tiles = {4} # The Sign ID

# A static map layout represented by tile IDs.
# 1=grass, 5=dirt_path
map_layout = [
    [1, 1, 1, 1, 5, 5, 5, 5, 5, 5, 1, 1, 1],
    [1, 1, 1, 5, 5, 1, 1, 1, 5, 5, 1, 1, 1],
    [1, 1, 5, 5, 1, 1, 1, 1, 1, 5, 5, 1, 1],
    [1, 5, 5, 1, 1, 1, 1, 1, 1, 1, 5, 5, 1],
    [5, 5, 1, 1, 1, 1, 1, 1, 1, 1, 1, 5, 5],
    [5, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 5],
    [5, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 5],
    [5, 5, 1, 1, 1, 1, 1, 1, 1, 1, 1, 5, 5],
    [1, 5, 5, 1, 1, 1, 1, 1, 1, 1, 5, 5, 1],
    [1, 1, 5, 5, 5, 5, 5, 5, 5, 5, 5, 1, 1],
]

# Data for interactive signs, mapping (y, x) coordinates to text.
map_signs = {
    (4, 6): ["A weathered sign...", "'Beware the Slimes'"]
}

# Data for interactive objects, mapping (y, x) to tile ID and text.
map_objects = {
    (6, 6): (52, ["You found a", "strange, glowing", "crystal."])
}
```

- `game_assets\templar_data.py`
```
"" 

```

- `game_assets\templar_rooms.py`
```
from cpgame.game_assets.templar_data import bounce, bounceH
bounce = { None: [(bounce, bounceH, 0, 0, 3, 3, 1, 1, 50), (bounce, bounceH, 3, 0, 5, 5, 2, 2, 50), (bounce, bounceH, 8, 0, 7, 7, 3, 3, 50), (bounce, bounceH, 15, 0, 11, 11, 5, 5, 50), (bounce, bounceH, 26, 0, 5, 5, 2, 2, 50)] }
room_level1 = (21, 15, b'\x03!!!!!!!!!!!!!!!!!\x04\x04\x05\x13\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x10\x13\xff\xff\xff\xff\xff\xff\xff\t\n\x0b\xff\xff\xff\xff\xff\xffe\xff\xff\x10\x12\xff\xff\xff\xff\xff\xff\xff\x19\x11\x1b\xff\xff\xff\xff\xff\xff6\xff\xff\x10\x12\xff\xff\xff\xff\xff\xff\xff)*+\xff\xff\xff\xff\xff\xff\xff\xff\xff\x10\x12\xff\xff\xff\xffe\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x10\x12\xff\xff\xff789\xff\xff\xff\xffe\xff\xff\xff\xff\xff\xff\xff\xff\x10\x12\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff6cccc6\xff\xff\xff\x10\x12e\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x10\x12b\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x10\x12\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xffe\x10X9\xff\xff\xff\xff\xff`\xff\xff\xff\xff\xff\xff\xff\xff\xff\xffa7Y\x12\xff\xff\xff\xffa\x00\x01\x02\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x10\x12\xff\xff\xff\xff\xff\x10\x11\x12RRR:\xff\xffe\xff\xff\xff\xff\x10#\x01\x01\x01\x01%\x11#\x01\x01\x01\x01I\x01\x01\x01\x01\x01\x01\x01%')

room_levels = [
    room_level1
]
```

- `game_scenes\__init__.py`
```

```

- `game_scenes\jrpg_scene.py`
```
# scenes/jrpg_scene.py
# A top-down, tile-based RPG scene.

from gint import *
try:
    from typing import Optional, List, Set, Tuple, Dict
except:
    pass

# Engine imports
from cpgame.engine.scene import Scene
from cpgame.engine.systems import Camera # Although we manage it manually here

# --- Scene Constants ---
TILE_SIZE = 20
MOVE_DELAY = 0.15 # Seconds between player steps

class JRPGScene(Scene):
    """
    Implements the top-down exploration gameplay.
    Features grid-based movement, a block-based camera, and a dialog system.
    """
    def __init__(self, game):
        super().__init__(game)

        # --- Game State ---
        self.player_x: int = 0
        self.player_y: int = 0
        self.move_cooldown: float = 0.0

        # --- Map Data (loaded in create) ---
        self.tileset = None
        self.map_layout: List[List[int]] = []
        self.map_objects: Dict[Tuple[int, int], Tuple[int, List[str]]] = {}
        self.map_signs: Dict[Tuple[int, int], List[str]] = {}
        self.map_w: int = 0
        self.map_h: int = 0

        # --- Special Camera Control ---
        # This scene uses a non-standard "block" camera
        self.cam_block_x: int = -1
        self.cam_block_y: int = -1
        self.screen_tiles_x = DWIDTH // TILE_SIZE
        self.screen_tiles_y = DHEIGHT // TILE_SIZE

        # --- Rendering Optimization ---
        self.dirty_tiles: Set[Tuple[int, int]] = set()
        self.full_redraw_needed: bool = True

        # --- Dialog System State ---
        self.dialog_active: bool = False
        self.dialog_pages: List[str] = []
        self.dialog_index: int = 0

    def create(self):
        """
        Called once by the game loop when this scene starts.
        Responsible for loading assets and setting up initial state.
        """
        print("JRPGScene: Creating...")

        # Load all necessary assets from the manager
        self.tileset = self.assets.tilesets["jrpg"]
        map_asset = self.assets.maps["jrpg_village"]
        self.map_layout = map_asset["layout"]
        self.map_objects = map_asset["objects"]
        self.map_signs = map_asset["signs"]
        self.map_h = len(self.map_layout)
        self.map_w = len(self.map_layout[0])

        # Set player's starting position
        self.player_x = self.map_w // 2
        self.player_y = self.map_h // 2

        # Initialize the camera's first position
        self._update_camera_block()
        self.full_redraw_needed = True

    def update(self, dt: float) -> Optional[str]:
        """
        Main logic update, called every fixed timestep.
        """
        # First, poll the input state for this frame
        self.input.update()

        # --- State Machine: Are we in a dialog or exploring? ---
        if self.dialog_active:
            self._update_dialog()
            return None # Prevent any other game logic from running

        # --- Exploring State Logic ---
        # Handle scene transitions first
        if self.input.exit:
            # We import here to avoid circular dependency issues
            from cpgame.game_scenes.menu_scene import MenuScene
            return self.game.change_scene(MenuScene)

        # Update timers
        if self.move_cooldown > 0:
            self.move_cooldown -= dt

        # Handle player input for movement and interaction
        self._handle_player_movement()
        self._handle_player_interaction()

        return None

    def draw(self, frame_time_ms: int):
        """
        Main drawing function, called every render frame.
        """
        if self.full_redraw_needed:
            self._draw_viewport()
            self.full_redraw_needed = False
        elif self.dirty_tiles:
            for tx, ty in self.dirty_tiles:
                self._draw_tile_at(tx, ty)

        self.dirty_tiles.clear()

        self._draw_player()

        if self.dialog_active:
            self._draw_dialog_box()

    # --- Private Update Helpers ---

    def _update_dialog(self):
        """Handles input logic when a dialog box is active."""
        if self.input.interact:
            self.dialog_index += 1
            if self.dialog_index >= len(self.dialog_pages):
                # Dialog has ended
                self.dialog_active = False
                self.full_redraw_needed = True # Redraw the world underneath

    def _handle_player_movement(self):
        """Checks for and processes player movement input."""
        if self.move_cooldown > 0:
            return

        # Use dx/dy for direction, but only move one direction at a time
        dx, dy = 0, 0
        if self.input.dx > 0: dx = 1
        elif self.input.dx < 0: dx = -1
        elif self.input.dy > 0: dy = 1
        elif self.input.dy < 0: dy = -1
        
        if dx == 0 and dy == 0:
            return

        next_x, next_y = self.player_x + dx, self.player_y + dy

        if self._is_walkable(next_x, next_y):
            old_pos = (self.player_x, self.player_y)
            self.player_x, self.player_y = next_x, next_y
            
            self.move_cooldown = MOVE_DELAY # Reset timer
            
            # Mark tiles for redraw
            self.dirty_tiles.add(old_pos)
            self.dirty_tiles.add((self.player_x, self.player_y))
            
            # Check if the camera needs to move to a new screen block
            if self._update_camera_block():
                self.full_redraw_needed = True

    def _handle_player_interaction(self):
        """Checks for interaction with objects or signs."""
        if not self.input.interact:
            return

        # Check for objects on the player's current tile
        player_pos = (self.player_y, self.player_x)
        if player_pos in self.map_objects:
            _, pages = self.map_objects[player_pos]
            self._start_dialog(pages)
            return

        # Check for signs on adjacent tiles
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            adj_pos = (self.player_y + dy, self.player_x + dx)
            if adj_pos in self.map_signs:
                pages = self.map_signs[adj_pos]
                self._start_dialog(pages)
                return

    def _is_walkable(self, x: int, y: int) -> bool:
        """Checks if a given map coordinate is within bounds and not a solid tile."""
        if not (0 <= y < self.map_h and 0 <= x < self.map_w):
            return False
        
        tile_id = self.map_layout[y][x]
        return tile_id not in self.tileset.solid # type: ignore

    def _update_camera_block(self) -> bool:
        """
        Updates the camera to a new screen-sized "block" if the player has moved into one.
        Returns True if the camera moved, False otherwise.
        """
        new_block_x = self.player_x // self.screen_tiles_x
        new_block_y = self.player_y // self.screen_tiles_y

        if new_block_x != self.cam_block_x or new_block_y != self.cam_block_y:
            self.cam_block_x = new_block_x
            self.cam_block_y = new_block_y
            self.camera.x = self.cam_block_x * self.screen_tiles_x * TILE_SIZE
            self.camera.y = self.cam_block_y * self.screen_tiles_y * TILE_SIZE
            return True
        return False

    def _start_dialog(self, pages: List[str]):
        """Initializes the dialog system."""
        self.dialog_active = True
        self.dialog_pages = pages
        self.dialog_index = 0

    # --- Private Drawing Helpers ---

    def _world_to_screen(self, world_x: int, world_y: int) -> Tuple[int, int]:
        """Converts world tile coordinates to screen pixel coordinates."""
        return (world_x * TILE_SIZE - self.camera.x, world_y * TILE_SIZE - self.camera.y)

    def _draw_viewport(self):
        """Performs a full redraw of all visible tiles on the screen."""
        dclear(C_BLACK)
        base_x = self.cam_block_x * self.screen_tiles_x
        base_y = self.cam_block_y * self.screen_tiles_y

        # Iterate one tile beyond the screen edge to avoid pop-in
        for ry in range(self.screen_tiles_y + 1):
            for rx in range(self.screen_tiles_x + 1):
                map_x, map_y = base_x + rx, base_y + ry
                if 0 <= map_y < self.map_h and 0 <= map_x < self.map_w:
                    self._draw_tile_at(map_x, map_y)

    def _draw_tile_at(self, map_x: int, map_y: int):
        """Redraws a single tile on the map, including any object on it."""
        screen_x, screen_y = self._world_to_screen(map_x, map_y)
        
        # Culling: Don't draw if it's off-screen
        if not (-TILE_SIZE < screen_x < DWIDTH and -TILE_SIZE < screen_y < DHEIGHT):
            return

        # Draw base map tile
        tile_id = self.map_layout[map_y][map_x]
        src_x = (tile_id % 16) * TILE_SIZE
        src_y = (tile_id // 16) * TILE_SIZE
        dsubimage(screen_x, screen_y, self.tileset.img, src_x, src_y, TILE_SIZE, TILE_SIZE) # type: ignore

        # Draw object on top, if any
        pos = (map_y, map_x)
        if pos in self.map_objects:
            obj_id, _ = self.map_objects[pos]
            obj_src_x = (obj_id % 16) * TILE_SIZE
            obj_src_y = (obj_id // 16) * TILE_SIZE
            dsubimage(screen_x, screen_y, self.tileset.img, obj_src_x, obj_src_y, TILE_SIZE, TILE_SIZE) # type: ignore

    def _draw_player(self):
        """Draws the player representation on the screen."""
        scr_x, scr_y = self._world_to_screen(self.player_x, self.player_y)
        center_x = scr_x + TILE_SIZE // 2
        center_y = scr_y + TILE_SIZE // 2
        dcircle(center_x, center_y, TILE_SIZE // 2 - 2, C_BLUE, C_NONE)

    def _draw_dialog_box(self):
        """Draws the UI for the dialog box at the bottom of the screen."""
        box_h = DHEIGHT // 4
        y0 = DHEIGHT - box_h
        drect(0, y0, DWIDTH - 1, DHEIGHT - 1, C_WHITE)
        drect_border(0, y0, DWIDTH - 1, DHEIGHT - 1, C_NONE, 1, C_BLACK)

        if self.dialog_index < len(self.dialog_pages):
            page_text = self.dialog_pages[self.dialog_index]
            for i, line in enumerate(page_text.split("\n")):
                dtext(8, y0 + 8 + i * 16, C_BLACK, line)

```

- `game_scenes\menu_scene.py`
```
# scenes/menu_scene.py
# The initial scene that lets the player choose a game.
from gint import *
from cpgame.engine.scene import Scene
from cpgame.game_scenes.templar_scene import TemplarScene
from cpgame.game_scenes.jrpg_scene import JRPGScene

C_YELLOW = 0b00000_111111_11111

class MenuScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.options = ["Play Platformer (Templar)", "Play Top-Down (JRPG)", "Exit"]
        self.selected_index = 0
        self.redraw_needed = True

    def update(self, dt: float) -> None:
        """Update is called once per logic frame."""
        # Get a snapshot of the input for this frame.
        self.input.update()

        # Use the new one-shot `up` and `down` properties for snappy menu navigation.
        if self.input.up:
            self.selected_index = (self.selected_index - 1 + len(self.options)) % len(self.options)
            self.redraw_needed = True
        
        if self.input.down:
            self.selected_index = (self.selected_index + 1) % len(self.options)
            self.redraw_needed = True
        
        # Check for the interact button press to make a selection.
        if self.input.interact:
            if self.selected_index == 0:
                self.game.change_scene(TemplarScene)
            elif self.selected_index == 1:
                self.game.change_scene(JRPGScene)
            elif self.selected_index == 2:
                self.game.running = False # Signal the game to exit
        
        # Also allow exiting with the EXIT key.
        if self.input.exit:
            self.game.running = False

    def draw(self, frame_time_ms: int):
        """Draw is called once per render frame."""
        # Only redraw the screen if something has changed.
        if not self.redraw_needed:
            return
            
        dclear(C_RGB(2, 5, 10))
        dtext_opt(DWIDTH//2, 50, C_WHITE, C_NONE, DTEXT_CENTER, DTEXT_TOP, "CPGAME ENGINE DEMO", -1)
        
        for i, option in enumerate(self.options):
            color = C_YELLOW if i == self.selected_index else C_WHITE
            dtext_opt(DWIDTH//2, 150 + i * 25, color, C_NONE, DTEXT_CENTER, DTEXT_TOP, option, -1)
            
        self.redraw_needed = False
```

- `game_scenes\templar_scene.py`
```
# scenes/templar_scene.py
# The complete Templar platformer game, refactored into a Scene.

from gint import *
try:
    from typing import Optional, Tuple, List, Dict, Any, Generator
except:                         # MicroPython or stripped env
    pass

# Engine imports
from cpgame.engine.scene import Scene
from cpgame.engine.geometry import Vec2, Rect
from cpgame.engine.animation import AnimationState
from cpgame.engine.assets import Tilemap, AssetManager

# --- Scene-Specific Constants ---
# We use fixed-point math to avoid floats. All positions and speeds are
# scaled up by 2^8, and then scaled down for rendering.
FIXED_POINT_SHIFT = 8

# Viewport and HUD layout
WW, WH = 21, 15
MAP_X, MAP_Y = -8, -8
HUD_X, HUD_Y, HUD_W, HUD_H = 320, 0, 76, 224

# Player and physics states
STANCE_IDLE, STANCE_RUNNING, STANCE_JUMPING, STANCE_HURT, STANCE_VICTORY = 0, 1, 2, 3, 4
FACING_LEFT, FACING_RIGHT = 0, 1
PH_GROUNDED, PH_LWALL, PH_RWALL, PH_HEADBANG, PH_TOO_FAST, PH_FAILED, PH_DEATH = 1, 2, 4, 8, 16, 32, 64
SOLID_STD, SOLID_PLANK, SOLID_INTERACTIBLE, SOLID_DEATH, SOLID_NOT, SOLID_FLAG = 0, 1, 2, 3, 4, 5


# --- Templar-Specific Data Structures ---
# These classes are tightly coupled with this scene's logic.

class playerT:
    """Holds all state for the player character."""
    def __init__(self):
        self.pos: Vec2 = Vec2(0,0)
        self.speed: Vec2 = Vec2(0,0)
        self.stance: int = -1
        self.facing: int = FACING_RIGHT
        self._grounded: bool = True
        self.jump_frames: int = 0
        self.jump_buffer: int = 0
        self.noncontrol_frames: int = 0
        self.anim: AnimationState = AnimationState()

    def initialize(self, pos: Vec2):
        # Initial position is in pixels, so we scale it up to fixed-point.
        self.pos = Vec2(pos.x, pos.y)
        self.speed = Vec2(0, 0)

    def grounded(self) -> bool: return self._grounded
    def airborne(self) -> bool: return not self._grounded

class roomT:
    """Holds all data for a single level or room."""
    def __init__(self, w: int, h: int, spawn_x: int, spawn_y: int, tileset: Tilemap, flag_sequence: List):
        self.w, self.h = w, h
        self.tiles: Optional[bytes] = None
        self.tile_collisions: Optional[bytearray] = None
        self.spawn_x, self.spawn_y = spawn_x, spawn_y
        self.tileset = tileset
        self.flag_sequence = flag_sequence

    def tile_solid(self, tileID: int) -> bool:
        return tileID != 0xff and self.tileset.solid[tileID] == SOLID_STD

    def alignToTiles(self, wr: Rect) -> Tuple[int, int, int, int]:
        # Convert fixed-point Rect to tile grid coordinates
        x1 = max(int(wr.x) >> 4, 0)
        x2 = min(int(wr.x + wr.w - 1) >> 4, self.w - 1)
        y1 = max(int(wr.y) >> 4, 0)
        y2 = min(int(wr.y + wr.h - 1) >> 4, self.h - 1)
        return x1, y1, x2, y2

    def hitboxesNear(self, wr: Rect) -> Generator[Tuple[Rect, int, int], None, None]:
        if not self.tiles or not self.tile_collisions: return
        x1, y1, x2, y2 = self.alignToTiles(wr)
        tb = self.tileset.tileboxes
        for y in range(y1, y2 + 1):
            for x in range(x1, x2 + 1):
                i = self.w * y + x
                t = self.tiles[i]
                if t != 0xff and tb[4*t+2]:
                    yield Rect(
                        (16*x + tb[4*t]),
                        (16*y + tb[4*t+1]),
                        tb[4*t+2],
                        tb[4*t+3]
                    ), self.tile_collisions[i], self.tileset.solid[t]

    def compute_tile_collisions(self):
        if not self.tiles: return
        w, h = self.w, self.h; i = 0
        self.tile_collisions = bytearray(w * h)
        for y in range(h):
            for x in range(w):
                t = self.tiles[i]
                solid = SOLID_NOT if t == 0xff else self.tileset.solid[t]
                if solid == SOLID_PLANK:
                    if y > 0 and not self.tile_solid(self.tiles[i - w]):
                        self.tile_collisions[i] = PH_GROUNDED
                elif solid != SOLID_NOT:
                    sides = 0
                    if y > 0 and not self.tile_solid(self.tiles[i - w]): sides |= PH_GROUNDED
                    if y < h-1 and not self.tile_solid(self.tiles[i+w]): sides |= PH_HEADBANG
                    if x > 0 and not self.tile_solid(self.tiles[i-1]): sides |= PH_RWALL
                    if x < w-1 and not self.tile_solid(self.tiles[i+1]): sides |= PH_LWALL
                    self.tile_collisions[i] = sides
                i += 1

# --- The Main Templar Scene Class ---

class TemplarScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        # --- Game State Attributes ---
        self.room: Optional[roomT] = None
        self.player: Optional[playerT] = None
        self.entities: List[Tuple[Vec2, AnimationState]] = []
        self.flags_data: Dict[Tuple[int, int], bool] = {}
        self.flags_taken: int = 0
        self.flag_cursor: int = 0
        self.dirty_tiles: Optional[bytearray] = None
        self.game_time: float = 0.0
        self.deaths: int = 0
        self.reset_timer: float = -1.0
        self.end_timer: float = -1.0
        self.physics_flags: int = 0
        self.debug_hitboxes: int = 0
        self.debug_resolution: Rect = Rect(0,0,0,0)
        # --- Asset References ---
        self.tileset: Optional[Tilemap] = None
        self.animations: Dict = {}

    def create(self):
        """Initializes the game state, called once when the scene starts."""
        print("TemplarScene: Creating...")
        
        # Load assets from the manager
        self.tileset = self.assets.tilesets["templar"]
        self.animations = self.assets.animations
        
        # Setup level
        from cpgame.game_assets.templar_data import room_level1 # Load specific room data
        flag_sequence = [(15, 13, 1), (19, 10, 2), (11, 6, 1), (5, 5, 1), (17, 2, 0), (1, 8, 0)]
        self.room = roomT(WW, WH, 32, 224, self.tileset, flag_sequence) # type: ignore
        self.room.tiles = room_level1[2]
        self.room.compute_tile_collisions()

        # Setup player
        self.player = playerT()
        self.player.initialize(Vec2(self.room.spawn_x, self.room.spawn_y))
        self.player_set_stance(STANCE_IDLE)

        # Setup rendering state
        self.dirty_tiles = bytearray(self.room.w * self.room.h)
        for i in range(len(self.dirty_tiles)): self.dirty_tiles[i] = 1
        
        self.show_next_flags(1)

    def update(self, dt: float) -> Optional[str]:
        """Handles all game logic and input for one fixed-step update."""
        assert self.player and self.room and self.dirty_tiles is not None

        self.input.update() # Polls gint for the latest input state

        if self.input.exit:
            from cpgame.game_scenes.menu_scene import MenuScene
            self.game.change_scene(MenuScene)
            return
        
        dx = self.input.dx
        jump_down = keydown(KEY_SHIFT) or keydown(KEY_UP)
        if self.input.shift or self.input.up: self.player.jump_buffer = 3
        
        if keypressed(KEY_KBD):
            self.debug_hitboxes = (self.debug_hitboxes + 1) % 3
            # Mark all tiles dirty to redraw hitbox outlines
            for i in range(len(self.dirty_tiles)): self.dirty_tiles[i] = 1

        # --- Update Game State Timers ---
        self.game_time += dt
        self.player.anim.update(dt)

        # Update entities and remove finished ones
        self.entities = [e for e in self.entities if not e[1].update(dt)]

        if self.end_timer > 0:
            self.end_timer -= dt
            if self.end_timer <= 0: return "EXIT_GAME"
        
        if self.reset_timer > 0:
            self.reset_timer -= dt
            if self.reset_timer <= 0:
                self.reset_timer = -1
                self.player.initialize(Vec2(self.room.spawn_x, self.room.spawn_y))
                self.deaths += 1

        # --- Player Physics (Integer-based) ---
        if self.player.jump_buffer > 0: self.player.jump_buffer -= 1
        
        # Jumping
        if self.player.jump_buffer and self.player.grounded():
            self.player.speed.y = -140
            self.player.jump_frames = 5
            self.player.jump_buffer = 0

        # Horizontal Movement & Friction
        self.player.speed.x *= 0.97
        if self.input.dx > 0: self.player.speed.x = max(self.player.speed.x, 64)
        elif self.input.dx < 0: self.player.speed.x = min(self.player.speed.x, -64)
        else: self.player.speed.x //= 2 ## int(self.player.speed.x * 0.5)
        
        # Vertical Movement & Gravity
        if self.player.airborne(): self.player.speed.y += 9.81 * dt * 30
        if self.player.jump_frames > 0:
            # jump_down = keydown(KEY_SHIFT) or keydown(KEY_UP)
            if not jump_down: self.player.speed.y = max(self.player.speed.y, -20)
            self.player.jump_frames -= 1

        # Update stance and facing direction
        self.player_set_stance(STANCE_JUMPING if self.player.airborne() else (STANCE_RUNNING if self.input.dx else STANCE_IDLE))
        if self.input.dx > 0: self.player.facing = FACING_RIGHT
        elif self.input.dx < 0: self.player.facing = FACING_LEFT

        # --- Collision and Displacement ---
        self.player.pos, self.physics_flags = self.physics_displace(self.player.pos, self.player.speed * dt) # type: ignore -- it is supported my __mul__
        self.player._grounded = (self.physics_flags & PH_GROUNDED) != 0

        # React to collision flags
        if self.physics_flags & (PH_LWALL | PH_RWALL): self.player.speed.x = 0
        if self.physics_flags & PH_HEADBANG: self.player.speed.y = max(self.player.speed.y, 0)
        if self.physics_flags & PH_GROUNDED: self.player.speed.y = 20 # Push gently into the ground

        # Check for death or out of bounds
        is_out_of_bounds = not (0 < self.player.pos.x < 16*self.room.w and 0 < self.player.pos.y < 16*self.room.h)
        if (self.physics_flags & PH_DEATH) or is_out_of_bounds:
            self.player_set_stance(STANCE_HURT)
            self.reset_timer = 0.6
        
        # Check for victory
        if self.flags_taken >= len(self.room.flag_sequence) and self.end_timer < 0:
            self.player_set_stance(STANCE_VICTORY)
            self.end_timer = 3.0
        return None

    def draw(self, frame_time_ms: int):
        """Renders the entire game world."""
        assert self.player and self.room and self.dirty_tiles is not None
        
        self.draw_room()
        for pos, entity_anim in self.entities:
            self.draw_entity(pos, entity_anim)
        self.draw_player()
        self.draw_hud(frame_time_ms)

        # Debug visualizations
        if self.debug_hitboxes >= 1:
            phb = self.physics_player_hitbox(self.player.pos)
            self.draw_outline(self.debug_resolution, C_RGB(0,31,0))
            self.draw_outline(phb, C_GREEN)
        if self.debug_hitboxes == 2:
            full_room_rect = Rect(0, 0, self.room.w << 4, self.room.h << 4)
            for b, bf, _ in self.room.hitboxesNear(full_room_rect):
                self.draw_flagged_outline(b, bf, C_RED, C_WHITE)

    # --- Scene-specific Helper Methods ---
    def player_set_stance(self, stance: int):
        assert self.player
        if self.player.stance == stance: return
        self.player.stance = stance
        if stance == STANCE_IDLE: self.player.anim.set(self.animations["Idle"])
        elif stance == STANCE_RUNNING: self.player.anim.set(self.animations["Running"])
        elif stance == STANCE_JUMPING: self.player.anim.set(self.animations["Jumping"])
        elif stance == STANCE_HURT: self.player.anim.set(self.animations["Hurt"])
        elif stance == STANCE_VICTORY: self.player.anim.set(self.animations["Victory"])

    def physics_player_hitbox(self, pos: Vec2) -> Rect:
        return Rect(pos.x - 5, pos.y - 14, 11, 14)

    def physics_acceptable(self, pos: Vec2) -> bool:
        assert self.room
        player_hb = self.physics_player_hitbox(pos)
        for hb, _, solid in self.room.hitboxesNear(player_hb):
            if solid == SOLID_STD and player_hb.intersects(hb):
                # HACK: Backwards world to tile grid conversion
                x, y = int(hb.x) >> 4, int(hb.y) >> 4
                # TODO: game.takeFlag(x, y)
                return False
        return True

    def physics_displace(self, pos: Vec2, diff: Vec2) -> Tuple[Vec2, int]:
        pr = self.physics_player_hitbox(pos + diff)
        resolution = Vec2(0, 0); flags = 0
        if self.room:
            for r, rf, solid in self.room.hitboxesNear(pr):
                if not pr.intersects(r): continue
                if solid == SOLID_DEATH: return pos + diff, PH_DEATH
                if solid in (SOLID_NOT, SOLID_FLAG): continue
                
                player_top_pixel = pos.y
                plank_top_pixel = r.top
                if solid == SOLID_PLANK and (diff.y < 0 or player_top_pixel > plank_top_pixel + 1): continue
                
                left_overlap = max(r.right - pr.left, 0)
                right_overlap = min(r.left - pr.right, 0)
                top_overlap = max(r.bottom - pr.top, 0)
                bottom_overlap = min(r.top - pr.bottom, 0)
                
                smallest_overlap = 999999
                xo, yo, fo = 0.0, 0.0, 0
                
                if (rf & PH_LWALL) and 0 < left_overlap < smallest_overlap:
                    xo, yo, fo, smallest_overlap = left_overlap, 0, PH_LWALL, left_overlap
                if (rf & PH_RWALL) and 0 < -right_overlap < smallest_overlap:
                    xo, yo, fo, smallest_overlap = right_overlap, 0, PH_RWALL, -right_overlap
                if (rf & PH_HEADBANG) and 0 < top_overlap < smallest_overlap:
                    xo, yo, fo, smallest_overlap = 0, top_overlap, PH_HEADBANG, top_overlap
                if (rf & PH_GROUNDED) and 0 < -bottom_overlap < smallest_overlap:
                    xo, yo, fo, smallest_overlap = 0, bottom_overlap, PH_GROUNDED, -bottom_overlap
                
                if abs(xo) > abs(resolution.x): resolution.x = xo # type: ignore
                if abs(yo) > abs(resolution.y): resolution.y = yo # type: ignore
                flags |= fo
            
        self.debug_resolution = self.physics_player_hitbox(pos + diff + resolution)
        if max(abs(resolution.x), abs(resolution.y)) >= 15: return pos, PH_TOO_FAST
        
        adjusted = pos + diff
        if not (flags & PH_LWALL and flags & PH_RWALL): adjusted.x += resolution.x
        if not (flags & PH_HEADBANG and flags & PH_GROUNDED): adjusted.y += resolution.y
        
        return (adjusted, flags) if self.physics_acceptable(adjusted) else (pos, flags | PH_FAILED)
    
    def mark_tiles_dirty(self, wr: Rect):
        assert self.dirty_tiles
        assert self.room

        x1, y1, x2, y2 = self.room.alignToTiles(wr)
        for y in range(y1, y2 + 1):
            for x in range(x1, x2 + 1): self.dirty_tiles[y * self.room.w + x] = 1

    def show_next_flags(self, n: int):
        assert self.room
        n = min(n, len(self.room.flag_sequence) - self.flag_cursor)
        for _ in range(n):
            x, y, _ = self.room.flag_sequence[self.flag_cursor]
            self.flags_data[(x, y)] = False
            if self.dirty_tiles:
                self.dirty_tiles[y * self.room.w + x] = 1
            self.flag_cursor += 1

    def draw_room(self):
        assert self.room
        i = 0
        if self.room.tiles:
            for ty in range(self.room.h):
                for tx in range(self.room.w):
                    t = self.room.tiles[i]
                    if t == 101 and self.flags_data.get((tx, ty), True): t = 0xff
                    if self.dirty_tiles and self.dirty_tiles[i]:
                        self.draw_tile(tx, ty, t)
                        self.dirty_tiles[i] = 0
                    i += 1
    
    def draw_tile(self, x: int, y: int, tileID: int):
        assert self.room
        assert self.tileset
        img = self.room.tileset.img # self.tileset.img ?
        sx, sy = MAP_X + 16 * x, MAP_Y + 16 * y
        w = img.width >> 4; tx, ty = tileID % w, tileID // w
        dsubimage(sx, sy, img, 176, 48, 16, 16) # background
        if 16 * ty < img.height:
            dsubimage(sx, sy, img, 16 * tx, 16 * ty, 16, 16)

    def draw_player(self):
        assert self.player
        p = self.player
        flipped = (p.facing == FACING_LEFT)
        base = self.world2screen(p.pos)

        # base_x = (p.pos.x) + MAP_X
        # base_y = (p.pos.y) + MAP_Y

        if p.anim.index >= 0 and p.anim.frames:
            f = p.anim.frames[p.anim.index]
            img, cx = (f.imgH, f.w - 1 - f.cx) if flipped else (f.img, f.cx)
            draw_x, draw_y = base.x - cx, base.y - f.cy
            dsubimage(draw_x, draw_y, img, f.x, f.y, f.w, f.h)
            self.mark_tiles_dirty(self.screen2world_rect(Rect(draw_x, draw_y, f.w, f.h)))

    def draw_entity(self, pos: Vec2, anim: AnimationState):
        base = self.world2screen(pos)
        # base_x = (pos.x >> FIXED_POINT_SHIFT) + MAP_X
        # base_y = (pos.y >> FIXED_POINT_SHIFT) + MAP_Y
        if anim.index >= 0  and anim.frames:
            f = anim.frames[anim.index]
            draw_x, draw_y = base.x - f.cx, base.y - f.cy
            dsubimage(draw_x, draw_y, f.img, f.x, f.y, f.w, f.h)
            self.mark_tiles_dirty(self.screen2world_rect(Rect(draw_x, draw_y, f.w, f.h)))

    def draw_hud(self, frame_time_ms: int):
        x, y = HUD_X + 2, HUD_Y + 4
        drect(HUD_X, HUD_Y, HUD_X + HUD_W - 1, HUD_Y + HUD_H - 1, C_RGB(6,5,2))
        if self.debug_hitboxes > 0:
            dtext_opt(x, y+135, C_WHITE, C_NONE, DTEXT_LEFT, DTEXT_TOP, f"ft: {frame_time_ms} ms", -1)
        else:
            if self.room:
                dtext_opt(x, y, C_WHITE, C_NONE, DTEXT_LEFT, DTEXT_TOP, f"Flags: {self.flags_taken}/{len(self.room.flag_sequence)}", -1)
            dtext_opt(x, y+15, C_WHITE, C_NONE, DTEXT_LEFT, DTEXT_TOP, f"Deaths: {self.deaths}", -1)
            dtext_opt(x, y+30, C_WHITE, C_NONE, DTEXT_LEFT, DTEXT_TOP, f"Time: {self.game_time:.1f}", -1)

    def world2screen(self, pos: Vec2) -> Vec2:
        return Vec2(MAP_X + int(pos.x), MAP_Y + int(pos.y))
    def world2screen_rect(self, r: Rect) -> Rect:
        return Rect(MAP_X + int(r.x), MAP_Y + int(r.y), int(r.w), int(r.h))
    def screen2world_rect(self, r: Rect) -> Rect:
        return Rect(r.x - MAP_X, r.y - MAP_Y, r.w, r.h)
    
    def draw_outline(self, r: Rect, color: int):
        self.mark_tiles_dirty(r)
        r = self.world2screen_rect(r)
        drect_border(r.x, r.y, r.x+r.w-1, r.y+r.h-1, C_NONE, 1, color)
    
    def draw_flagged_outline(self, r: Rect, rb: int, c1: int, c2: int):
        self.mark_tiles_dirty(r)
        r = self.world2screen_rect(r)
        x1 = (r.x) + MAP_X
        y1 = (r.y) + MAP_Y
        x2 = ((r.x + r.w)) + MAP_X
        y2 = ((r.y + r.h)) + MAP_Y
        # dline(x1,y1,x2,y1, c2 if rb & PH_GROUNDED else c1)
        # dline(x1,y2,x2,y2, c2 if rb & PH_HEADBANG else c1)
        # dline(x1,y1,x1,y2, c2 if rb & PH_RWALL else c1)
        # dline(x2,y1,x2,y2, c2 if rb & PH_LWALL else c1)
        dline(r.x,r.y,r.x+r.w-1,r.y, c2 if rb & PH_GROUNDED else c1)
        dline(r.x,r.y+r.h-1,r.x+r.w-1,r.y+r.h-1, c2 if rb & PH_HEADBANG else c1)
        dline(r.x,r.y,r.x,r.y+r.h-1, c2 if rb & PH_RWALL else c1)
        dline(r.x+r.w-1,r.y,r.x+r.w-1,r.y+r.h-1, c2 if rb & PH_LWALL else c1)


```

