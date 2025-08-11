import gint
from gui.dialog import DialogResult, GUIDialog, GUIDialogHeight, GUIDialogAlignment, GUIDialogKeyboardState
from gui.label import GUILabel
from gui.button import GUIButton

# Constants for clarity
BUTTON_CLOSE_EVENT_ID = 1042

class DemoDialog(GUIDialog):
    def __init__(self):
        # Create a dialog 25% height, centered, no keyboard
        super().__init__(
            GUIDialogHeight.Height25,
            GUIDialogAlignment.AlignTop,
            "Demo Dialog Name",
            GUIDialogKeyboardState.KeyboardStateNone
        )
        # Greeting label
        self.greet_label = GUILabel(
            self.GetLeftX() + 2,
            self.GetTopY() + 2,
            "Hello Dialog World !"
        )
        # Close button
        self.close_btn = GUIButton(
            self.GetLeftX(),
            self.GetBottomY() - 35,
            self.GetLeftX() + 96,
            self.GetBottomY() - 3,
            "Close",
            BUTTON_CLOSE_EVENT_ID
        )
        # Add elements to the dialog
        self.AddElement(self.greet_label)
        self.AddElement(self.close_btn)
    
    def OnEvent(self, event_id):
        if event_id == BUTTON_CLOSE_EVENT_ID:
            print("Got button click :)")
            return DialogResult.OK


dialog = DemoDialog()
result = dialog.ShowDialog()
gint.dclear(gint.C_WHITE)
gint.dupdate()
print("Dialog closed with result:", result)
