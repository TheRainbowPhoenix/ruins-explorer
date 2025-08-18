# cpgame/game_windows/window_message.py
# The window that displays the content of GameMessage.
from gint import *
from cpgame.game_windows.window_base import WindowBase
from cpgame.systems.jrpg import JRPG
from cpgame.engine.text_parser import parse_text_codes

class WindowMessage(WindowBase):
    def __init__(self):
        height = 100 # Default height
        super().__init__(0, DHEIGHT - height, DWIDTH, height)
        self.openness = 0
        self.visible = False
        self._text_progress = 0
        self._wait_for_input = False

    def update(self):
        super().update()
        if JRPG.objects and JRPG.objects.message.is_busy():
            self.visible = True
            # Simple "opening" animation
            if self.openness < 255: self.openness = min(255, self.openness + 32)
            
            # Check for input to close the message
            # if self._wait_for_input and JRPG.input.interact:
            #     self.terminate_message()

        else:
            if self.openness > 0: self.openness = max(0, self.openness - 32)
            if self.openness == 0: self.visible = False

    def on_confirm(self):
        """
        Called by the scene when the player presses the interact button.
        This is the correct way to handle input, decoupling the window from the input system.
        """
        if self.is_ready_for_input():
            self.terminate_message()

    def is_ready_for_input(self) -> bool:
        """Checks if the message is fully open and waiting for input."""
        return self.visible and self.openness >= 255 and self._wait_for_input

    def terminate_message(self):
        """Closes the window and clears the central message data."""
        self.openness = 0
        self.visible = False
        self._wait_for_input = False
        if JRPG.objects: JRPG.objects.message.clear()

    def draw(self):
        if not self.visible or self.openness < 255:
            return
            
        super().draw() # Draw window skin
        
        if not JRPG.objects: return
        message = JRPG.objects.message
        
        # Draw text lines
        for i, line in enumerate(message.texts):
            final_text = parse_text_codes(line)
            dtext(self.x + self.padding, self.y + self.padding + i * 16, C_BLACK, final_text)

        # Draw continue triangle
        self._wait_for_input = True
        tri_x = self.x + self.width - self.padding - 10
        tri_y = self.y + self.height - self.padding - 10
        dline(tri_x, tri_y, tri_x + 5, tri_y - 5, C_BLACK)
        dline(tri_x + 5, tri_y - 5, tri_x + 10, tri_y, C_BLACK)
        dline(tri_x + 10, tri_y, tri_x, tri_y, C_BLACK)