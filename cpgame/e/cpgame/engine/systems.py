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
