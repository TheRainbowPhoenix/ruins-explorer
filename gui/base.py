import gint

try:
    from typing import List, Optional
except:
    pass

from .rect import Rect

def hex_to_rgb(color):
    r8 = (color >> 16) & 0xFF
    g8 = (color >> 8) & 0xFF
    b8 = color & 0xFF

    r5 = r8 >> 3
    g5 = g8 >> 3
    b5 = b8 >> 3

    return (r5 << 10) | (g5 << 5) | b5

class GUIEvent:
    """A universal event object for all UI interactions."""
    def __init__(self, type, source: 'Widget', **kwargs):
        self.type = type      # e.g., "touch_down", "key_press", "click"
        self.source = source  # The widget that originated the event
        self.handled = False
        # self.__dict__.update(kwargs) # TODO: this fails on PythonExtra !!
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __str__(self):
        return f"GUIEvent(type={self.type}, source={self.source.__class__.__name__})"

# --- Core Widget ---

class Widget:
    """The base class for all UI elements."""
    def __init__(self, x=0, y=0, width=0, height=0):
        self.rect = Rect(x, y, x + width - 1, y + height - 1)
        self.parent: Optional['Widget'] = None
        self.children: List[Widget] = []
        self.visible = True
        self.enabled = True
        self._needs_redraw = True
    
    def on_focus_gained(self) -> None:
        """Called when the widget receives keyboard focus."""
        pass
        
    def on_focus_lost(self) -> None:
        """Called when the widget loses keyboard focus."""
        pass

    def set_needs_redraw(self, value=True):
        """Mark this widget and its parents as needing to be redrawn."""
        self._needs_redraw = value
        if self.parent and value:
            self.parent.set_needs_redraw(True)

    def add_child(self, child):
        """Add a child widget."""
        if child not in self.children:
            self.children.append(child)
            child.parent = self
            self.set_needs_redraw()

    def remove_child(self, child):
        """Remove a child widget."""
        if child in self.children:
            self.children.remove(child)
            child.parent = None
            self.set_needs_redraw()

    def get_absolute_rect(self):
        """Calculate the widget's absolute screen position."""
        if not self.parent:
            return self.rect.copy()
        parent_rect = self.parent.get_absolute_rect()
        abs_x = parent_rect.left + self.rect.left
        abs_y = parent_rect.top + self.rect.top
        return Rect(abs_x, abs_y, abs_x + self.rect.width - 1, abs_y + self.rect.height - 1)

    def handle_event(self, event: GUIEvent):
        """
        Handle an event. Propagate to children unless handled.
        Returns True if the event was handled.
        """
        if not self.visible or not self.enabled:
            return False

        # Dispatch to children first (top-most widgets get first dibs)
        for child in reversed(self.children):
            if child.handle_event(event):
                return True
        
        # If no child handled it, try to handle it itself
        if self.on_event(event):
            return True

        return False

    def on_event(self, event: GUIEvent):
        """
        Event handler to be overridden by subclasses.
        Return True to mark the event as handled.
        """
        return False

    def draw(self):
        """Draw the widget and its children."""
        if not self.visible:
            return

        # Let the widget draw itself
        self.on_draw()

        # Recursively draw children
        for child in self.children:
            child.draw()
        
        self._needs_redraw = False

    def on_draw(self):
        """Drawing logic to be overridden by subclasses."""
        pass # Base widget has no visual representation

    def find_widget_at(self, x, y):
        """Find the topmost child widget at a given point (absolute coordinates)."""
        if not self.visible or not self.get_absolute_rect().contains(x, y):
            return None

        # Check children in reverse (top-most first)
        for child in reversed(self.children):
            found = child.find_widget_at(x, y)
            if found:
                return found
        
        return self # This widget is the one

# --- Application Runner ---

class Application:
    """Manages the main event loop and the root widget."""
    def __init__(self, root_widget):
        self.root = root_widget
        self.focused_widget: Optional[Widget] = None
        self.frame_count = 0

    def set_focus(self, widget: Optional[Widget]) -> None:
        """Sets the focus to a new widget, notifying both old and new."""
        if self.focused_widget is widget:
            return
            
        if self.focused_widget:
            self.focused_widget.on_focus_lost()
            
        self.focused_widget = widget
        
        if self.focused_widget:
            self.focused_widget.on_focus_gained()

    def run(self):
        """Starts the main application event loop."""
        while True:
            self.frame_count += 1
            if self.frame_count % 30 == 0 and self.focused_widget:
                if hasattr(self.focused_widget, 'cursor_visible'):
                    self.focused_widget.cursor_visible = not self.focused_widget.cursor_visible # type: ignore
                    self.focused_widget.set_needs_redraw()
            
            # Full redraw if needed
            if self.root._needs_redraw:
                gint.dclear(gint.C_WHITE)
                self.root.draw()
                gint.dupdate()

            ev = gint.pollevent()
            if ev.type == gint.KEYEV_NONE:
                continue

            # Create a standard GUIEvent
            event = None
            source_widget = self.root.find_widget_at(getattr(ev, 'x', -1), getattr(ev, 'y', -1)) or self.root

            if ev.type == gint.KEYEV_TOUCH_DOWN:
                self.set_focus(source_widget)

            if ev.type == gint.KEYEV_DOWN:
                if ev.key == gint.KEY_EXIT:
                    break # Exit application on EXIT key
                if self.focused_widget:
                    event = GUIEvent("key_press", self.focused_widget, key=ev.key)
                    self.focused_widget.handle_event(event)
                    continue # Skip normal propagation
                else: # No focus, propagate normally
                    event = GUIEvent("key_press", source_widget, key=ev.key)

            elif ev.type == gint.KEYEV_TOUCH_DOWN:
                event = GUIEvent("touch_down", source_widget, pos=(ev.x, ev.y))
            
            elif ev.type == gint.KEYEV_TOUCH_UP:
                event = GUIEvent("touch_up", source_widget, pos=(ev.x, ev.y))

            elif ev.type == gint.KEYEV_TOUCH_DRAG:
                event = GUIEvent("touch_drag", source_widget, pos=(ev.x, ev.y))

            # Dispatch the event
            if event:
                self.root.handle_event(event)

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