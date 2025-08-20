# Contains helper systems like Input and Camera.

from gint import *

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

        self.nexp: bool = False
        self.n0: bool = False
        self.n1: bool = False
        self.n2: bool = False
        self.n3: bool = False
        self.n4: bool = False
        self.n5: bool = False
        self.n6: bool = False
        self.n7: bool = False
        self.n8: bool = False
        self.n9: bool = False

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

        # Numpad
        self.nexp = keypressed(KEY_EXP)
        self.n0 = keypressed(KEY_0)
        self.n1 = keypressed(KEY_1)
        self.n2 = keypressed(KEY_2)
        self.n3 = keypressed(KEY_3)
        self.n4 = keypressed(KEY_4)
        self.n5 = keypressed(KEY_5)
        self.n6 = keypressed(KEY_6)
        self.n7 = keypressed(KEY_7)
        self.n8 = keypressed(KEY_8)
        self.n9 = keypressed(KEY_9)  

    def is_repeat(self, code: str):
        if code == 'down':
            return keydown(KEY_DOWN) and not self.down
        if code == 'up':
            return keydown(KEY_UP) and not self.up
        if code == 'right':
            return keydown(KEY_RIGHT) and not self.right
        if code == 'left':
            return keydown(KEY_LEFT) and not self.left
        
        return False

    def is_trigger(self, code: str):
        """ Used for proxying inputs. Use this later for custom keymap"""
        if code == 'confirm':
            return self.interact
        if code == 'cancel':
            return self.shift or self.exit
        if code == 'page_down':
            return self.n3
        if code == 'page_up':
            return self.n9
        
        if code == 'down':
            return self.down
        if code == 'up':
            return self.up
        if code == 'right':
            return self.right
        if code == 'left':
            return self.left
        
        return False

class Camera:
    """A basic camera that can be used by scenes."""
    def __init__(self, x: int = 0, y: int = 0):
        self.x = x
        self.y = y
