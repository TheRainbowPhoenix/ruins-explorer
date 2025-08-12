import gint
import time
from collections import namedtuple

C_LIGHT = 0xD69A
C_DARK = 0xAD55

# --- Constants from the C implementation ---
# Alignment
J_ALIGN_LEFT = 0
J_ALIGN_CENTER = 1
J_ALIGN_RIGHT = 2
J_ALIGN_TOP = 0
J_ALIGN_MIDDLE = 1
J_ALIGN_BOTTOM = 2

# Border Styles
J_BORDER_NONE = 0
J_BORDER_SOLID = 1

# --- Helper Functions and Classes ---

# A simple font representation for calculations until gint provides more.
# We'll assume a basic fixed-width font for now.
class Font:
    def __init__(self, width, height, line_spacing=2):
        self.char_width = width
        self.line_height = height
        self.line_distance = height + line_spacing

# Let's assume a default font is available
# On fx-CG, the small font is 6x8. Medium is 8x8 (or 12x12).
DEFAULT_FONT = Font(8, 12)

# A simple rect for culling calculations
VisibleRect = namedtuple('VisibleRect', ['x1', 'y1', 'x2', 'y2'])

class JEvent:
    """A simple event class to replace the C struct."""
    def __init__(self, type, source=None, **kwargs):
        self.type = type
        self.source = source
        # self.__dict__.update(kwargs) # TODO: this fails on PythonExtra !!
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __repr__(self):
        # Filter out internal-looking attributes for a cleaner representation
        attrs = {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
        return f"JEvent({attrs})"

# Event Types (we'll add more as we implement more widgets)
JWIDGET_KEY = 0x1000 # gint.j_register_event()
JWIDGET_FOCUS_CHANGED = 0x1001 # gint.j_register_event()

class JWidget:
    """Base class for all widgets, equivalent to the C jwidget struct."""

    def __init__(self, parent=None):
        self._parent = None
        self._children = []
        
        # Geometry and position
        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0
        self.min_w, self.min_h = 0, 0
        self.max_w, self.max_h = 32767, 32767

        # Layout and appearance
        self._layout = None
        self.stretch_x = 0
        self.stretch_y = 0
        self.visible = True
        self._clipped = False
        
        # Box model properties
        self._margins = {'top': 0, 'right': 0, 'bottom': 0, 'left': 0}
        self._borders = {'top': 0, 'right': 0, 'bottom': 0, 'left': 0}
        self._padding = {'top': 0, 'right': 0, 'bottom': 0, 'left': 0}
        self._border_color = gint.C_NONE
        self._background_color = gint.C_NONE
        
        # State flags
        self._dirty = True  # Needs layout recalculation
        self._update = True # Needs redraw

        if parent:
            self.set_parent(parent)

    def set_parent(self, parent):
        if self._parent:
            self._parent.remove_child(self)
        self._parent = parent
        if self._parent:
            self._parent.add_child(self)

    def add_child(self, child):
        if child not in self._children:
            self._children.append(child)
            child._parent = self
            self.mark_dirty()

    def remove_child(self, child):
        if child in self._children:
            self._children.remove(child)
            child._parent = None
            self.mark_dirty()

    def mark_dirty(self):
        """Mark this widget and all its ancestors as needing a layout recalculation."""
        self._dirty = True
        if self._parent:
            self._parent.mark_dirty()

    def mark_for_update(self):
        """Mark this widget and its ancestors for redraw."""
        self._update = True
        if self._parent:
            self._parent.mark_for_update()

    def needs_update(self):
        if self._update:
            return True
        for child in self._children:
            if child.visible and child.needs_update():
                return True
        return False

    def set_layout(self, layout):
        self._layout = layout
        self.mark_dirty()

    def set_fixed_size(self, w, h):
        self.min_w, self.max_w = w, w
        self.min_h, self.max_h = h, h
        self.mark_dirty()

    def set_stretch(self, x, y):
        self.stretch_x = x
        self.stretch_y = y
        self.mark_dirty()

    def set_padding(self, top, right, bottom, left):
        self._padding = {'top': top, 'right': right, 'bottom': bottom, 'left': left}
        self.mark_dirty()

    def set_border(self, width, color):
        self._borders = {'top': width, 'right': width, 'bottom': width, 'left': width}
        self._border_color = color
        self.mark_dirty()
        
    def set_background(self, color):
        self._background_color = color
        self.mark_for_update()

    @property
    def content_width(self):
        return self.w - (self._margins['left'] + self._borders['left'] + self._padding['left'] +
                         self._padding['right'] + self._borders['right'] + self._margins['right'])

    @property
    def content_height(self):
        return self.h - (self._margins['top'] + self._borders['top'] + self._padding['top'] +
                         self._padding['bottom'] + self._borders['bottom'] + self._margins['bottom'])

    def _get_full_box_size(self):
        """Calculate total size including geometry."""
        width = (self._margins['left'] + self._borders['left'] + self._padding['left'] +
                 self._padding['right'] + self._borders['right'] + self._margins['right'])
        height = (self._margins['top'] + self._borders['top'] + self._padding['top'] +
                  self._padding['bottom'] + self._borders['bottom'] + self._margins['bottom'])
        return width, height

    # --- "Virtual" methods for subclasses to override ---

    def _csize(self):
        """Calculate natural content size. Overridden by subclasses."""
        # For a generic widget with no layout, size is the bounding box of its children.
        max_x, max_y = 0, 0
        for child in self._children:
            if child.visible:
                child._csize()
                max_x = max(max_x, child.x + child.w)
                max_y = max(max_y, child.y + child.h)
        self.w, self.h = max_x, max_y

    def _layout_phase1(self):
        """Internal recursive method for Phase 1 layout."""
        # Bottom-up: process children first
        for child in self._children:
            if child.visible:
                child._layout_phase1()

        # Calculate this widget's natural size
        if self._layout:
            self._layout.csize(self)
        else:
            self._csize() # Let the widget's own logic decide
            
        # Add geometry to get full size
        geom_w, geom_h = self._get_full_box_size()
        self.w += geom_w
        self.h += geom_h


    def _layout_phase2(self, w, h):
        """Internal recursive method for Phase 2 layout."""
        self.w = max(self.min_w, min(w, self.max_w))
        self.h = max(self.min_h, min(h, self.max_h))
        
        if self._layout:
            self._layout.apply(self)
        
        # Top-down: after setting our size, layout children
        for child in self._children:
            if child.visible:
                child._layout_phase2(child.w, child.h)
        
        self._dirty = False

    def _render(self, x, y, visible_rect):
        """Render the widget. Overridden by subclasses."""
        if not self.visible:
            return

        # 1. Render background
        if self._background_color != gint.C_NONE:
            bg_x = x + self._margins['left'] + self._borders['left']
            bg_y = y + self._margins['top'] + self._borders['top']
            bg_w = self.w - (self._margins['left'] + self._margins['right'] + self._borders['left'] + self._borders['right'])
            bg_h = self.h - (self._margins['top'] + self._margins['bottom'] + self._borders['top'] + self._borders['bottom'])
            gint.drect(bg_x, bg_y, bg_x + bg_w - 1, bg_y + bg_h - 1, self._background_color)
            
        # 2. Render border
        if self._border_color != gint.C_NONE:
            b_x = x + self._margins['left']
            b_y = y + self._margins['top']
            b_w = self.w - (self._margins['left'] + self._margins['right'])
            b_h = self.h - (self._margins['top'] + self._margins['bottom'])
            # This is a simplified drect_border
            gint.drect_border(b_x, b_y, b_x+b_w-1, b_y+b_h-1, gint.C_NONE, self._borders['top'], self._border_color)

        # 3. Calculate content area
        content_x = x + self._margins['left'] + self._borders['left'] + self._padding['left']
        content_y = y + self._margins['top'] + self._borders['top'] + self._padding['top']

        # 4. Let the subclass render its specific content
        self._render_content(content_x, content_y, visible_rect)

        # 5. Render children
        for child in self._children:
            child._render(content_x + child.x, content_y + child.y, visible_rect)
        
        self._update = False

    def _render_content(self, x, y, visible_rect):
        """The specific rendering implementation for a subclass."""
        pass # Base widget has no content to render

    def _event(self, event):
        """Handle an event. Overridden by subclasses. Return True if handled."""
        return False

    def handle_event(self, event):
        """Dispatch an event, bubbling up the hierarchy."""
        for child in reversed(self._children):
            if child.handle_event(event):
                return True
        # If no child handled it, try to handle it itself
        return self._event(event)


class JScene(JWidget):
    """The root of the widget tree, managing the event loop and rendering."""
    def __init__(self):
        super().__init__()
        self.w, self.h = gint.DWIDTH, gint.DHEIGHT
        self._running = False
        self._focused_widget = self # By default, the scene itself is focused

    def set_focus(self, widget):
        # TODO: Implement full focus change events
        self._focused_widget = widget

    def layout(self):
        if not self._dirty:
            return
        self._layout_phase1()
        self._layout_phase2(self.w, self.h)

    def render(self):
        # The scene's visible rect is the entire screen
        visible_rect = VisibleRect(0, 0, gint.DWIDTH, gint.DHEIGHT)
        self._render(0, 0, visible_rect)
        gint.dupdate()

    def run(self):
        """The main application loop."""
        self._running = True
        while self._running:
            # Layout and Rendering
            if self._dirty:
                self.layout()
                self.mark_for_update()

            if self.needs_update():
                self.render()

            # Event Handling
            ev = gint.pollevent()
            if ev.type != gint.KEYEV_NONE:
                if ev.type == gint.KEYEV_DOWN and ev.key == gint.KEY_MENU:
                    # Default exit behavior
                    self.stop()
                    continue
                
                # For now, dispatch all key events to the scene itself
                # Later, this will go to the focused widget
                if self._focused_widget:
                    self._focused_widget.handle_event(JEvent(JWIDGET_KEY, key_event=ev))

            time.sleep_ms(10) # Small sleep to prevent busy-waiting

    def stop(self):
        self._running = False

# --- Layout Managers ---

class VBoxLayout:
    def __init__(self, spacing=0):
        self.spacing = spacing

    def csize(self, widget):
        """Calculate natural size for a vertical box."""
        total_h = 0
        max_w = 0
        visible_children = [c for c in widget._children if c.visible]
        
        if visible_children:
            total_h = (len(visible_children) - 1) * self.spacing
            for child in visible_children:
                max_w = max(max_w, child.w)
                total_h += child.h
        
        widget.w, widget.h = max_w, total_h

    def apply(self, widget):
        """Distribute space and position children vertically."""
        # This is a simplified version of the C code's flex-like distribution.
        # It currently does not handle stretch factors.
        y_pos = 0
        content_w = widget.content_width
        
        for child in widget._children:
            if not child.visible:
                continue
            
            # Simple centering for now
            child.x = (content_w - child.w) // 2
            child.y = y_pos
            y_pos += child.h + self.spacing


# --- Concrete Widgets ---

class JLabel(JWidget):
    """A text label widget."""
    def __init__(self, text="", parent=None, font=DEFAULT_FONT):
        super().__init__(parent)
        self.text = text
        self.font = font
        self.color = gint.C_BLACK
        self.wrap_mode = 'word' # 'none', 'word', 'char'
        self._lines = [] # For wrapped text

    def _csize(self):
        """Calculate size based on text content."""
        self._lines = self._wrap_text(self.text, self.w or gint.DWIDTH) # Use widget width if available
        
        if not self._lines:
            self.w, self.h = 0, 0
            return
            
        max_line_width = max(len(line) * self.font.char_width for line in self._lines)
        
        self.w = max_line_width
        self.h = len(self._lines) * self.font.line_height

    def _wrap_text(self, text, max_width):
        """A simple word wrapper."""
        lines = []
        for paragraph in text.split('\n'):
            words = paragraph.split(' ')
            current_line = ""
            for word in words:
                if current_line and (len(current_line) + 1 + len(word)) * self.font.char_width >= max_width:
                    lines.append(current_line)
                    current_line = word
                else:
                    if current_line:
                        current_line += ' '
                    current_line += word
            lines.append(current_line)
        return lines

    def _render_content(self, x, y, visible_rect):
        # Recalculate wrapping based on final allocated width
        self._lines = self._wrap_text(self.text, self.content_width)
        
        line_y = y
        for line in self._lines:
            # Check if the line is vertically within the visible area before drawing
            if line_y + self.font.line_height > visible_rect.y1 and line_y < visible_rect.y2:
                gint.dtext(x, line_y, self.color, line)
            line_y += self.font.line_height


class JFrame(JWidget):
    """A scrolling frame containing a single child."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._scroll_x = 0
        self._scroll_y = 0
        self._clipped = True # Frames are clipped by default
        self.set_border(1, gint.C_BLACK)
        self._is_dragging = False
        self._last_touch_y = 0

    def _render(self, x, y, parent_visible_rect):
        # We override the entire render method to implement scrolling and clipping.
        if not self.visible:
            return

        content_x = x + self._margins['left'] + self._borders['left'] + self._padding['left']
        content_y = y + self._margins['top'] + self._borders['top'] + self._padding['top']
        content_w = self.content_width
        content_h = self.content_height
        
        # This frame's new visible rectangle for its children
        # It's the intersection of its own content area and its parent's visible area
        frame_visible_rect = VisibleRect(
            max(content_x, parent_visible_rect.x1),
            max(content_y, parent_visible_rect.y1),
            min(content_x + content_w, parent_visible_rect.x2),
            min(content_y + content_h, parent_visible_rect.y2)
        )

        # Render background and border first
        super()._render(x, y, parent_visible_rect)

        if not self._children: return
        child = self._children[0]
        
        # TODO: Clipping is not available in gint's Python API yet.
        # This is where we would set the clipping window.
        # gint.dwindow_set(...)
        
        # Render the child at a scrolled offset
        child_render_x = content_x - self._scroll_x
        child_render_y = content_y - self._scroll_y
        child._render(child_render_x, child_render_y, frame_visible_rect)

        # TODO: Restore clipping window
        # gint.dwindow_set(...)

        # Render scrollbars
        self._render_scrollbars(content_x, content_y, content_w, content_h, child)
        
        self._update = False

    def _render_scrollbars(self, x, y, w, h, child):
        scrollbar_width = 4
        # Vertical scrollbar
        if child.h > h:
            sb_h = max(10, h * h // child.h)
            sb_y = y + (self._scroll_y * (h - sb_h) // (child.h - h))
            sb_x = x + w - scrollbar_width
            gint.drect(sb_x, y, sb_x + scrollbar_width - 1, y + h - 1, C_LIGHT)
            gint.drect(sb_x, sb_y, sb_x + scrollbar_width - 1, sb_y + sb_h - 1, C_DARK)

    def _event(self, event):
        if event.type != JWIDGET_KEY:
            return False
            
        ev = event.key_event
        key = ev.key
        
        # --- Keyboard Scrolling ---
        if ev.type in (gint.KEYEV_DOWN, gint.KEYEV_HOLD):
            if key == gint.KEY_UP:
                self._scroll_y = max(0, self._scroll_y - 10)
                self.mark_for_update()
                return True
            if key == gint.KEY_DOWN:
                if self._children:
                    child = self._children[0]
                    max_scroll = max(0, child.h - self.content_height)
                    self._scroll_y = min(max_scroll, self._scroll_y + 10)
                    self.mark_for_update()
                    return True

        # --- Touchscreen Scrolling ---
        if ev.type == gint.KEYEV_TOUCH_DOWN:
            self._is_dragging = True
            self._last_touch_y = ev.y
            return True
        
        if ev.type == gint.KEYEV_TOUCH_DRAG and self._is_dragging:
            dy = ev.y - self._last_touch_y
            self._last_touch_y = ev.y
            
            # Invert scroll direction (drag down moves content up)
            self._scroll_y -= dy
            
            # Clamp scroll values
            if self._children:
                child = self._children[0]
                max_scroll = max(0, child.h - self.content_height)
                self._scroll_y = max(0, min(max_scroll, self._scroll_y))

            self.mark_for_update()
            return True
            
        if ev.type == gint.KEYEV_TOUCH_UP:
            self._is_dragging = False
            return True

        return False


# --- Example Usage ---

def main():
    # Setup
    scene = JScene()
    scene.set_background(gint.C_WHITE)

    # Create a frame to hold our scrollable content
    frame = JFrame(parent=scene)
    frame.set_fixed_size(200, 150)
    # Center the frame in the scene (simple manual layout for now)
    frame.x = (gint.DWIDTH - 200) // 2
    frame.y = (gint.DHEIGHT - 150) // 2
    frame.set_padding(5, 5, 5, 5)

    # Create a label with long text to demonstrate scrolling
    long_text = ("This is a demonstration of the JustUI port to MicroPython. "
                 "This label is inside a frame, which provides scrolling capabilities. "
                 "You can use the UP and DOWN arrow keys to scroll the text. "
                 "The layout system automatically calculates the required size for this text, "
                 "and the frame provides a viewport. "
                 "The text will wrap automatically if it is too long for a single line. "
                 "This showcases the JLabel, JFrame, and JScene working together. "
                 "More widgets like buttons and inputs will be added in the next phases.")
    label = JLabel(long_text, parent=frame)
    label.color = gint.C_BLACK
    # The label will stretch to the width of its parent frame's content area
    label.set_stretch(1, 0) 
    scene.set_focus(frame)
    
    # Run the application
    scene.run()

    # Cleanup
    gint.dclear(gint.C_WHITE)
    gint.dtext(10, 10, gint.C_BLACK, "Application finished.")
    gint.dupdate()
    time.sleep_ms(1000)

if __name__ == "__main__":
    # try:
    main()
    # except Exception as e:
    #     # Crude error handling for on-device debugging
    #     gint.dclear(gint.C_WHITE)
    #     gint.dtext(5, 5, gint.C_BLACK, f"Error: {e}")
    #     gint.dupdate()
    #     time.sleep_ms(5000)

