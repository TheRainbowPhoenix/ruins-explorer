# gui/frame.py
from .base import Widget
from .layouts import FrameLayout
from .toolbar import Toolbar
from .statusbar import StatusBar
from .menu import MenuBar
import gint

class MainFrame(Widget):
    """
    The main application frame, organizing the menu, toolbar, content, and status bar.
    """
    def __init__(self):
        super().__init__(0, 0, gint.DWIDTH, gint.DHEIGHT)
        
        # 1. Menu Bar
        self.menu_bar = MenuBar(0, 0, gint.DWIDTH)
        self.add_child(self.menu_bar)

        # 2. Toolbar
        self.toolbar = Toolbar(0, self.menu_bar.rect.height, gint.DWIDTH)
        self.add_child(self.toolbar)
        
        # 3. Status Bar
        self.status_bar = StatusBar(0, gint.DHEIGHT - 14, gint.DWIDTH)
        self.add_child(self.status_bar)
        
        # 4. Content Area
        content_y = self.menu_bar.rect.height + self.toolbar.rect.height
        content_height = gint.DHEIGHT - content_y - self.status_bar.rect.height
        self.content_area = FrameLayout(0, content_y, gint.DWIDTH, content_height)
        self.add_child(self.content_area)

        self.app_event_handler = self.dummy_event_handler

    def dummy_event_handler(self, ev):
        pass

    def on_event(self, event):
        """Listen for events to pass to a custom handler."""
        if hasattr(self, 'app_event_handler'):
            self.app_event_handler(event)
        return False # Always allow children to process events

    def add_panel(self, name, panel_widget):
        """Add a content panel to the content area."""
        self.content_area.add_child(panel_widget)
        panel_widget.visible = False # Hide by default
    
    def show_panel(self, panel_widget):
        """Show a specific panel in the content area."""
        self.content_area.show_child(panel_widget)