# demo_app.py
import gint
from gui.base import Application, Widget, GUIEvent
from gui.layouts import LinearLayout
from gui.frame import MainFrame
from gui.menu import Menu, MenuItem
from gui.button import Button
from gui.label import Label

try:
    from typing import Optional, List, Tuple
except ImportError:
    pass

C_LIGHT = 0xD69A

# --- Define Content Panels ---
# These are the different "screens" of our application.

class HomePanel(LinearLayout):
    """The main welcome screen."""
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, orientation=LinearLayout.VERTICAL, padding=5)
        self.add_child(Label(0, 0, "Welcome to the GUI Framework!"))
        self.add_child(Label(0, 0, "Use the menu to navigate."))
        self.add_child(Button(0, 0, 120, 25, "Go Page 2", event_id='nav_page2'))
        self.add_child(Button(0, 0, 120, 25, "Go Page 3", event_id='nav_page3'))

class Page2Panel(LinearLayout):
    """A second screen."""
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, orientation=LinearLayout.VERTICAL, padding=5)
        self.add_child(Label(0, 0, "This is the second page."))
        self.add_child(Button(0, 0, 120, 25, "Go Home", event_id='nav_home'))
        self.add_child(Button(0, 0, 120, 25, "Go Page 3", event_id='nav_page3'))

class Page3Panel(LinearLayout):
    """A second screen."""
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, orientation=LinearLayout.VERTICAL, padding=5)
        self.add_child(Label(0, 0, "This is the third page."))
        self.add_child(Button(0, 0, 120, 25, "Go Home", event_id='nav_home'))
        self.add_child(Button(0, 0, 120, 25, "Go Page 2", event_id='nav_page2'))

# Custom panel example
class PaintPanel(Widget):
    """A widget that acts as a simple drawing canvas."""

    def __init__(self, x: int, y: int, width: int, height: int):
        super().__init__(x, y, width, height)
        self.lines: List[Tuple[Tuple[int, int], Tuple[int, int]]] = []
        self.last_pos: Optional[Tuple[int, int]] = None

    def clear(self):
        """Clears all lines from the canvas."""
        self.lines.clear()
        self.set_needs_redraw()

    def on_event(self, event: GUIEvent) -> bool:
        # Only handle events that occurred within this widget's bounds.
        if event.source is not self:
            return False

        if event.type == "touch_down":
            self.last_pos = event.pos
            return True  # Consume the event

        if event.type == "touch_drag" and self.last_pos is not None:
            # We add the line segment to our list and request a redraw.
            # The coordinates are stored relative to the screen, not the widget.
            self.lines.append((self.last_pos, event.pos))
            self.last_pos = event.pos
            self.set_needs_redraw()
            return True

        if event.type == "touch_up":
            self.last_pos = None
            return True

        return False

    def on_draw(self) -> None:
        abs_rect = self.get_absolute_rect()

        # 1. Draw the background and border for the canvas.
        gint.drect(abs_rect.left, abs_rect.top, abs_rect.right, abs_rect.bottom, gint.C_WHITE)
        gint.drect_border(abs_rect.left, abs_rect.top, abs_rect.right, abs_rect.bottom, 
                          gint.C_NONE, 1, C_LIGHT)
        
        # 2. Redraw all the stored lines.
        for start, end in self.lines:
            gint.dline(start[0], start[1], end[0], end[1], gint.C_BLACK)

# --- Main Application Class ---

class DemoApp:
    def __init__(self):
        # Create the main application frame
        self.frame = MainFrame()
        self.frame.app_event_handler = self.handle_event

        # Create panels and add them to the frame's content area
        self.home_panel = HomePanel(0, 0, gint.DWIDTH, self.frame.content_area.rect.height)
        self.page2_panel = Page2Panel(0, 0, gint.DWIDTH, self.frame.content_area.rect.height)
        self.page3_panel = Page3Panel(0, 0, gint.DWIDTH, self.frame.content_area.rect.height)
        self.paint_panel = PaintPanel(0, 0, gint.DWIDTH, self.frame.content_area.rect.height)
        
        self.frame.add_panel('home', self.home_panel)
        self.frame.add_panel('page2', self.page2_panel)
        self.frame.add_panel('page3', self.page3_panel)
        self.frame.add_panel('paint', self.paint_panel)

        # Build the menu
        self.setup_menu()

        # Build the toolbar
        self.setup_toolbar()
        
        # Set the initial state
        self.frame.show_panel(self.home_panel)
        self.frame.status_bar.set_text("Application started.")
        
        # The main application runner
        self.app = Application(self.frame)

    def setup_menu(self):
        # File Menu
        
        new_map_submenu = Menu("New Map")
        new_map_submenu.add_item(MenuItem("Blank Map", event_id='file_new_map_blank'))
        new_map_submenu.add_item(MenuItem("From template...", event_id='file_new_map_template'))

        new_file_submenu = Menu("New File")
        new_file_submenu.add_item(MenuItem("Python Script", event_id='file_new_py'))
        new_file_submenu.add_item(MenuItem("Text Document", event_id='file_new_txt'))
        new_file_submenu.add_item(MenuItem("Map File", submenu=new_map_submenu))

        file_menu = Menu("File")
        file_menu.add_item(MenuItem("New", submenu=new_file_submenu))
        file_menu.add_item(MenuItem("Exit", event_id='file_exit'))
        self.frame.menu_bar.add_menu("File", file_menu)

        # View Menu
        view_menu = Menu("View")
        view_menu.add_item(MenuItem("Go to Home", event_id='nav_home'))
        view_menu.add_item(MenuItem("Go to Page 2", event_id='nav_page2'))
        view_menu.add_item(MenuItem("Go to Page 3", event_id='nav_page3'))
        view_menu.add_item(MenuItem("Paint", event_id='nav_paint'))
        self.frame.menu_bar.add_menu("View", view_menu)

        # Edit Menu to control Paint
        edit_menu = Menu("Edit")
        edit_menu.add_item(MenuItem("Clear Canvas", event_id='paint_clear'))
        self.frame.menu_bar.add_menu("Edit", edit_menu)
        
        # Add all menus as children to the frame for event processing
        self.frame.add_child(file_menu)
        self.frame.add_child(new_file_submenu)
        self.frame.add_child(new_map_submenu)
        self.frame.add_child(edit_menu)
        self.frame.add_child(view_menu)

    def setup_toolbar(self):
        # Toolbar buttons are just regular buttons added to the toolbar's layout
        home_btn = Button(0, 0, 50, 24, "Home", 'nav_home')
        page2_btn = Button(0, 0, 50, 24, "P2", 'nav_page2')
        page3_btn = Button(0, 0, 50, 24, "P3", 'nav_page3')
        paint_btn = Button(0, 0, 50, 24, "Paint", 'nav_paint')
        self.frame.toolbar.add_child(home_btn)
        self.frame.toolbar.add_child(page2_btn)
        self.frame.toolbar.add_child(page3_btn)
        self.frame.toolbar.add_child(paint_btn)

    def handle_event(self, event):
        """Central event handler for the application."""
        event_id = None
        if event.type == "click":
            event_id = event.button_id
        elif event.type == "menu_click":
            event_id = event.item_id
        
        if not event_id:
            return

        # --- Navigation ---
        if event_id == 'nav_home':
            self.frame.show_panel(self.home_panel)
            self.frame.status_bar.set_text("Switched to Home Panel.")
        
        elif event_id == 'nav_page2':
            self.frame.show_panel(self.page2_panel)
            self.frame.status_bar.set_text("Switched to Page 2.")
        
        elif event_id == 'nav_page3':
            self.frame.show_panel(self.page3_panel)
            self.frame.status_bar.set_text("Switched to Page 3.")
        
        elif event_id == 'nav_paint':
            self.frame.show_panel(self.paint_panel)
            self.frame.status_bar.set_text("Switched to Paint Panel. Drag to draw.")

        # Paint actions
        elif event_id == 'paint_clear':
            self.paint_panel.clear()
            self.frame.status_bar.set_text("Canvas cleared.")
        
        # --- File Actions ---
        elif event_id == 'file_new':
            self.frame.status_bar.set_text("Action: New File clicked!")
            
        elif event_id == 'file_new_py':
            self.frame.status_bar.set_text("Action: New Python Script!")
        elif event_id == 'file_new_txt':
            self.frame.status_bar.set_text("Action: New Text Document!")

        elif event_id == 'file_exit':
            # This is a bit of a hack to break the loop from outside
            # In a real app, the Application class would have a .quit() method
            gint.clearevents()
            gint.keydown(gint.KEY_EXIT) # Simulate exit key
            raise SystemExit()

    def run(self):
        try:
            self.app.run()
        except SystemExit:
            pass
        finally:
            gint.dclear(gint.C_WHITE)
            gint.dtext(5, 5, gint.C_BLACK, "Application terminated.")
            gint.dupdate()


demo = DemoApp()
demo.run()
    
        
