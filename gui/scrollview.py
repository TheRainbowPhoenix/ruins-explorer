# gui/scrollview.py
import gint
from .base import Widget, GUIEvent, set_scrollview_class
from .rect import Rect

try:
    from typing import Optional
except:
    pass

C_LIGHT_GRAY = 0xD69A
C_DARK_GRAY = 0xAD55
SCROLLBAR_WIDTH = 6

class ScrollView(Widget):
    """
    A viewport that can scroll a single, larger child widget.
    It handles touch dragging and keyboard arrows for navigation.
    """
    def __init__(self, x: int, y: int, width: int, height: int):
        super().__init__(x, y, width, height)
        self.child: Optional[Widget] = None
        self.scroll_x = 0
        self.scroll_y = 0

        self._is_dragging = False
        self._last_drag_pos = (0, 0)
        
        # Set a border to visually define the scroll area
        self.border_color = gint.C_BLACK
        self.background_color = gint.C_WHITE

    def add_child(self, child: Widget) -> None:
        """ScrollView can only contain one child. This replaces any existing child."""
        if self.child:
            super().remove_child(self.child)
        
        self.child = child
        # The child's position is relative to the scrollview's top-left corner
        child.rect.move_to(0, 0)
        super().add_child(child)
        self.set_needs_redraw()

    def _clamp_scroll(self):
        """Ensures scroll values are within valid bounds."""
        if not self.child:
            self.scroll_x = 0
            self.scroll_y = 0
            return

        max_scroll_x = max(0, self.child.rect.width - self.rect.width)
        max_scroll_y = max(0, self.child.rect.height - self.rect.height)

        if self.scroll_x < 0: self.scroll_x = 0
        if self.scroll_y < 0: self.scroll_y = 0
        if self.scroll_x > max_scroll_x: self.scroll_x = max_scroll_x
        if self.scroll_y > max_scroll_y: self.scroll_y = max_scroll_y
        
    def on_event(self, event: GUIEvent) -> bool:
        abs_rect = self.get_absolute_rect()
        # Only handle events that occurred within our bounds
        is_relevant_touch = hasattr(event, 'pos') and abs_rect.contains(event.pos[0], event.pos[1])

        if event.type == "touch_down" and is_relevant_touch:
            self._is_dragging = True
            self._last_drag_pos = event.pos
            return True

        if event.type == "touch_drag" and self._is_dragging:
            dx = event.pos[0] - self._last_drag_pos[0]
            dy = event.pos[1] - self._last_drag_pos[1]
            self._last_drag_pos = event.pos
            
            self.scroll_x -= dx
            self.scroll_y -= dy
            self._clamp_scroll()
            self.set_needs_redraw()
            return True

        if event.type == "touch_up":
            if self._is_dragging:
                self._is_dragging = False
                return True

        # --- Keyboard Scrolling ---
        if event.type == "key_press" and event.source is self:
            scroll_amount = 10
            scrolled = False
            if event.key == gint.KEY_UP:
                self.scroll_y -= scroll_amount
                scrolled = True
            elif event.key == gint.KEY_DOWN:
                self.scroll_y += scroll_amount
                scrolled = True
            elif event.key == gint.KEY_LEFT:
                self.scroll_x -= scroll_amount
                scrolled = True
            elif event.key == gint.KEY_RIGHT:
                self.scroll_x += scroll_amount
                scrolled = True
            
            if scrolled:
                self._clamp_scroll()
                self.set_needs_redraw()
                return True

        return False
    
    def draw(self, parent_clip_rect: Rect):
        """
        Overrides the default draw to implement hardware clipping for children.
        """
        if not self.visible:
            return

        my_abs_rect = self.get_absolute_rect()
        my_clip_rect = my_abs_rect.intersect(parent_clip_rect)

        if my_clip_rect.is_empty():
            return

        # 1. Draw the ScrollView's own frame (border, scrollbars, etc.)
        self.on_draw(my_clip_rect)

        # 2. Set up hardware clipping for the child content
        old_window = gint.dwindow_get()
        # The new window is the intersection of our area and the parent's clip area
        gint.dwindow_set(my_clip_rect.left, my_clip_rect.top, 
                         my_clip_rect.right + 1, my_clip_rect.bottom + 1)
        
        try:
            # 3. Draw children, which will now be clipped by the hardware window.
            # We still pass my_clip_rect so children know the software clip bounds.
            for child in self.children:
                child.draw(my_clip_rect)
        finally:
            # 4. CRITICAL: Always restore the previous clipping window
            gint.dwindow_set(old_window[0], old_window[1], old_window[2], old_window[3])

        self._needs_redraw = False

    def on_draw(self, clip_rect: Rect):
        """Draws the background, border, and scrollbars."""
        abs_rect = self.get_absolute_rect()
        
        # Draw background and a simple border
        gint.drect(abs_rect.left, abs_rect.top, abs_rect.right, abs_rect.bottom, self.background_color)
        gint.drect_border(abs_rect.left, abs_rect.top, abs_rect.right, abs_rect.bottom, 
                          gint.C_NONE, 1, self.border_color)

        if not self.child:
            return

        # --- Vertical Scrollbar ---
        view_h, child_h = self.rect.height, self.child.rect.height
        if child_h > view_h:
            # Scrollbar track
            sb_x = abs_rect.right - SCROLLBAR_WIDTH
            gint.drect(sb_x, abs_rect.top, abs_rect.right - 1, abs_rect.bottom - 1, C_LIGHT_GRAY)
            
            # Scrollbar thumb
            thumb_h = max(10, view_h * view_h / child_h)
            scrollable_h = child_h - view_h
            thumb_y_ratio = self.scroll_y / scrollable_h if scrollable_h > 0 else 0
            thumb_y = abs_rect.top + (thumb_y_ratio * (view_h - thumb_h))
            
            gint.drect(sb_x, int(thumb_y), abs_rect.right - 1, int(thumb_y + thumb_h) - 1, C_DARK_GRAY)
            
        # --- Horizontal Scrollbar (similar logic) ---
        view_w, child_w = self.rect.width, self.child.rect.width
        if child_w > view_w:
            sb_y = abs_rect.bottom - SCROLLBAR_WIDTH
            gint.drect(abs_rect.left, sb_y, abs_rect.right - 1, abs_rect.bottom - 1, C_LIGHT_GRAY)
            
            thumb_w = max(10, view_w * view_w / child_w)
            scrollable_w = child_w - view_w
            thumb_x_ratio = self.scroll_x / scrollable_w
            thumb_x = abs_rect.left + (thumb_x_ratio * (view_w - thumb_w))

            gint.drect(int(thumb_x), sb_y, int(thumb_x + thumb_w) - 1, abs_rect.bottom - 1, C_DARK_GRAY)

# This is a bit of a hack to solve the circular dependency between Widget and ScrollView.
# Call this from your main script before you create an Application instance.
set_scrollview_class(ScrollView)