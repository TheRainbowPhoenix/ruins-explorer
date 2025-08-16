import gint
from gui.base import Application, Widget
from gui.scrollview import ScrollView
from gui.layouts import VBox
from gui.label import Label
from gui.button import Button

# This handler function will be called when events bubble up to the root
def app_event_handler(event):
    if event.type == "click":
        # Check if the click came from our test button
        if hasattr(event, "button_id") and event.button_id == "test_button":
            print("Test button was clicked!")

def main():
    # 1. Create the root widget for the application.
    # We use a VBox to easily stack our main components vertically.
    root = VBox(padding=5)
    
    # Attach our custom event handler to the root
    root.app_event_handler = app_event_handler

    # 2. Add a standard button *outside* and above the scroll view
    test_button = Button(0, 0, 150, 25, "Test Button", event_id="test_button")
    root.add_child(test_button)
    
    # 3. Create the ScrollView, defining its size on the screen
    # Note: its position is (0,0) because the VBox layout will place it.
    scroll_view = ScrollView(0, 0, 250, 150)
    root.add_child(scroll_view)

    # 4. Create the content that will go *inside* the ScrollView.
    content = VBox(padding=5)
    
    # 5. Add widgets to the content panel to make it scrollable
    content.add_child(Label(0, 0, "--- Scrollable Content ---"))
    for i in range(20):
        # We give each button a unique ID for potential event handling
        btn = Button(0, 0, 200, 20, "Button Number {}".format(i+1), event_id="btn_{}".format(i))
        content.add_child(btn)
    content.add_child(Label(0, 0, "A Very Long Content Text that likes to talk a lot. Please shut up. I can't I have to talk a lot ! Do you now about the ... :) "))
    content.add_child(Label(0, 0, "--- End of Content ---"))

    # The layout calculates the required size for the content
    content.do_layout()

    # 6. Add the oversized content widget to the ScrollView
    scroll_view.add_child(content)
    
    # The root layout positions the button and scrollview
    root.do_layout()
    
    # 7. Run the application
    app = Application(root)
    # Set initial focus to the scroll view for keyboard input
    app.set_focus(scroll_view)
    app.run()


main()
gint.dclear(gint.C_WHITE)
gint.dtext(5, 5, gint.C_BLACK, "Application Closed")
gint.dupdate()