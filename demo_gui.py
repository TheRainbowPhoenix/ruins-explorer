# demo_app.py
import gint
from gui.base import Application, Widget
from gui.layouts import LinearLayout
from gui.frame import MainFrame
from gui.menu import Menu, MenuItem
from gui.button import Button
from gui.label import Label

# --- Define Content Panels ---
# These are the different "screens" of our application.

class HomePanel(LinearLayout):
    """The main welcome screen."""
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, orientation=LinearLayout.VERTICAL, padding=5)
        self.add_child(Label(0, 0, "Welcome to the GUI Framework!"))
        self.add_child(Label(0, 0, "Use the menu to navigate."))
        self.add_child(Button(0, 0, 120, 25, "Go Page 2", event_id='nav_page2'))

class Page2Panel(LinearLayout):
    """A second screen."""
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, orientation=LinearLayout.VERTICAL, padding=5)
        self.add_child(Label(0, 0, "This is the second page."))
        self.add_child(Button(0, 0, 120, 25, "Go Home", event_id='nav_home'))

# --- Main Application Class ---

class DemoApp:
    def __init__(self):
        # Create the main application frame
        self.frame = MainFrame()
        self.frame.app_event_handler = self.handle_event

        # Create panels and add them to the frame's content area
        self.home_panel = HomePanel(0, 0, gint.DWIDTH, self.frame.content_area.rect.height)
        self.page2_panel = Page2Panel(0, 0, gint.DWIDTH, self.frame.content_area.rect.height)
        
        self.frame.add_panel('home', self.home_panel)
        self.frame.add_panel('page2', self.page2_panel)

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
        file_menu = Menu("File")
        file_menu.add_item(MenuItem("New", event_id='file_new'))
        file_menu.add_item(MenuItem("Exit", event_id='file_exit'))
        self.frame.menu_bar.add_menu("File", file_menu)

        # View Menu
        view_menu = Menu("View")
        view_menu.add_item(MenuItem("Go to Home", event_id='nav_home'))
        view_menu.add_item(MenuItem("Go to Page 2", event_id='nav_page2'))
        self.frame.menu_bar.add_menu("View", view_menu)
        
        # Add all menus as children to the frame for event processing
        self.frame.add_child(file_menu)
        self.frame.add_child(view_menu)

    def setup_toolbar(self):
        # Toolbar buttons are just regular buttons added to the toolbar's layout
        home_btn = Button(0, 0, 50, 24, "Home", 'nav_home')
        page2_btn = Button(0, 0, 50, 24, "Page2", 'nav_page2')
        self.frame.toolbar.add_child(home_btn)
        self.frame.toolbar.add_child(page2_btn)

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

        # --- File Actions ---
        elif event_id == 'file_new':
            self.frame.status_bar.set_text("Action: New File clicked!")
            # Here you would open a dialog, for example.

        elif event_id == 'file_exit':
            # This is a bit of a hack to break the loop from outside
            # In a real app, the Application class would have a .quit() method
            gint.clearevents()
            gint.keydown(gint.KEY_EXIT) # Simulate exit key
            raise SystemExit()

    def run(self):
        self.app.run()


# --- Entry Point ---
if __name__ == "__main__":
    try:
        demo = DemoApp()
        demo.run()
    finally:
        # Ensure the screen is cleared on exit
        gint.dclear(gint.C_WHITE)
        gint.dtext(5, 5, gint.C_BLACK, "Application terminated.")
        gint.dupdate()
