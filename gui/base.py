import gint

def hex_to_rgb(color):
    r8 = (color >> 16) & 0xFF
    g8 = (color >> 8) & 0xFF
    b8 = color & 0xFF

    r5 = r8 >> 3
    g5 = g8 >> 3
    b5 = b8 >> 3

    return (r5 << 10) | (g5 << 5) | b5

class Wrapped:
    def __init__(self):
        self.children = []
        self.is_changed = True

    def Add(self, elem):
        self.children.append(elem)
        self.is_changed = True

    def do_draw(self):
        if not self.is_changed:
            return
        self.Draw()
        for child in self.children:
            child.Draw()
        self.is_changed = False
        self.EndDraw()
        gint.dupdate()

    def Draw(self):
        """Override in subclasses to draw the element."""
        pass

    def EndDraw(self):
        """Override for any post-draw actions."""
        pass

    def handleEvent(self, ev):
        return False
    
    def OnEvent(self, ev):
        pass

class GUIElement(Wrapped):
    def __init__(self, left, top, right, bottom, event_id=None, flags=0):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom
        self.bounds = (left, top, right, bottom)
        self.event_id = event_id
        self.flags = flags
        super().__init__()

    def render(self, canvas):
        raise NotImplementedError

    def handleEvent(self, ev):
        return False