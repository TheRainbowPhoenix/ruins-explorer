# Contains helper systems like Input and Camera.
import gc

import gint

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
        gint.cleareventflips()
        gint.clearevents()
        # Poll continuous state (`keydown`)
        self.dx = gint.keydown(gint.KEY_RIGHT) - gint.keydown(gint.KEY_LEFT)
        self.dy = gint.keydown(gint.KEY_DOWN) - gint.keydown(gint.KEY_UP)
        
        # Poll one-shot press state (`keypressed`)
        self.up = gint.keypressed(gint.KEY_UP)
        self.down = gint.keypressed(gint.KEY_DOWN)
        self.left = gint.keypressed(gint.KEY_LEFT)
        self.right = gint.keypressed(gint.KEY_RIGHT)
        self.interact = gint.keypressed(gint.KEY_EXE)
        self.menu = gint.keypressed(gint.KEY_MENU)
        self.exit = gint.keypressed(gint.KEY_EXIT)
        self.shift = gint.keypressed(gint.KEY_SHIFT)

        # Numpad
        self.nexp = gint.keypressed(gint.KEY_EXP)
        self.n0 = gint.keypressed(gint.KEY_0)
        self.n1 = gint.keypressed(gint.KEY_1)
        self.n2 = gint.keypressed(gint.KEY_2)
        self.n3 = gint.keypressed(gint.KEY_3)
        self.n4 = gint.keypressed(gint.KEY_4)
        self.n5 = gint.keypressed(gint.KEY_5)
        self.n6 = gint.keypressed(gint.KEY_6)
        self.n7 = gint.keypressed(gint.KEY_7)
        self.n8 = gint.keypressed(gint.KEY_8)
        self.n9 = gint.keypressed(gint.KEY_9) 

        if gint.keydown(gint.KEY_EQUALS):
            self._todo_debug_trace() 

        if gint.keydown(gint.KEY_LEFTPAR):
            self._todo_print_trace() 

    def is_repeat(self, code: str):
        if code == 'down':
            return gint.keydown(gint.KEY_DOWN) and not self.down
        if code == 'up':
            return gint.keydown(gint.KEY_UP) and not self.up
        if code == 'right':
            return gint.keydown(gint.KEY_RIGHT) and not self.right
        if code == 'left':
            return gint.keydown(gint.KEY_LEFT) and not self.left
        
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

    def _todo_debug_trace(self):
        gc.collect()
        free_mem = gc.mem_free()
        alloc_mem = gc.mem_alloc()
        txt = "{} + {}".format(alloc_mem,free_mem)
        
        gint.drect(0,0,gint.dsize(txt, None)[0], 12, gint.C_WHITE)
        gint.dtext(0,1,gint.C_BLUE, txt)


    def _todo_print_trace(self):
        gc.collect()
        free_mem = gc.mem_free()
        alloc_mem = gc.mem_alloc()
        txt = "{}/{}".format(alloc_mem,free_mem)
        print(txt)

class Camera:
    """A basic camera that can be used by scenes."""
    def __init__(self, x: int = 0, y: int = 0):
        self.x = x
        self.y = y

