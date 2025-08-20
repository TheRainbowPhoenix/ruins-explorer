# cpgame/game_windows/window_gold.py
# This window displays the party's gold.

from gint import *
from cpgame.game_windows.window_base import WindowBase
from cpgame.systems.jrpg import JRPG
from cpgame.engine.logger import log

class WindowGold(WindowBase):
    """A window that displays the party's current gold."""

    def __init__(self, x: int, y: int):
        # The window width is fixed, height fits one line.
        width = 160
        height = 40 
        super().__init__(x, y, width, height)

    def value(self) -> int:
        """Gets the current gold amount from the party object."""
        if JRPG.objects and JRPG.objects.party:
            return JRPG.objects.party.gold
        return 0

    def currency_unit(self) -> str:
        """Gets the currency unit string."""
        # In a full system, this would come from JRPG.data.system
        return "G"

    def refresh(self):
        """Redraws the contents of the window."""
        # In our direct-draw system, refresh is conceptually part of the draw call.
        self.draw()

    def draw(self):
        """Draws the window and its contents."""
        if not self.visible:
            return
        
        super().draw() # Draw the window skin

        # Draw the gold value, right-aligned
        value_text = str(self.value())
        unit_text = self.currency_unit()
        
        # Draw currency unit
        unit_width = len(unit_text) * 8 # Approximate width
        dtext(self.x + self.width - self.padding - unit_width, self.y + 4, C_BLACK, unit_text)

        # Draw value
        value_width = len(value_text) * 8
        dtext(self.x + self.width - self.padding - unit_width - value_width - 2, self.y + 4, C_BLACK, value_text)