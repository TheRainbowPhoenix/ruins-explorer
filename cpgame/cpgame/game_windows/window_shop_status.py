# cpgame/game_windows/window_shop_status.py
# Displays item possession count and actor equipment comparisons.

from gint import *
from cpgame.game_windows.window_base import WindowBase
from cpgame.systems.jrpg import JRPG
from cpgame.engine.text_parser import parse_text_codes

try:
    from typing import Optional
    from cpgame.game_objects.actor import GameActor
except: pass

class WindowShopStatus(WindowBase):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self._item = None
        self._actor = None # The actor to compare stats for
        self.visible = False

    def set_item(self, item):
        """Sets the item to be displayed and refreshes the window."""
        if self._item != item:
            self._item = item
            self.refresh()

    def refresh(self):
        """Clears and redraws the window's contents."""
        # In our direct-draw system, this is handled by the draw call
        pass

    def draw(self):
        if not self.visible: return
        super().draw()
        
        if not self._item or not JRPG.objects: return

        # Draw possession count
        item_count = JRPG.objects.party.item_number(self._item)
        dtext(self.x + self.padding, self.y + 4, C_BLACK, "Possess:")
        dtext(self.x + self.width - self.padding - 16, self.y + 4, C_BLACK, str(item_count))

        # If the item is equipment, draw comparison stats
        if self._item._category in ['weapons', 'armors']:
            # For simplicity, we compare against the party leader
            self._actor = JRPG.objects.party.leader()
            if not self._actor: return

            # Draw actor name
            dtext(self.x + self.padding, self.y + 30, C_BLACK, self._actor.name)

            # Draw current and new parameter values
            self._draw_actor_param_change(self.x + self.padding, self.y + 54)

    def _draw_actor_param_change(self, x, y):
        """Draws the stat comparison for an equipment piece."""
        
        if not self._item:
            return

        # For simplicity, we always compare ATK for weapons and DEF for armor
        param_id = 2 if self._item._category == 'weapons' else 3
        
        # Draw the parameter name (ATK or DEF)
        param_name = "ATK" if param_id == 2 else "DEF"
        dtext(x, y, C_BLACK, param_name)


        current_param = '-'
        new_param = '-'

        if self._actor:
            current_item = None
            for o in self._actor.equips_objects():
                if o.id == self._item.etype_id:
                    current_item = o
            
            current_param = self._actor.param(param_id)
            
            if current_item: 
                # Simulate equipping the new item
                change = self._item.params[param_id] - (current_item.params[param_id] if current_item else 0)
                new_param = current_param + change
        

        # Draw the current value
        dtext(x + 80, y, C_BLACK, str(current_param))

        # Draw the arrow
        dtext(x + 120, y, C_BLACK, "->")

        # Draw the new value with color coding
        color = C_BLACK
        if change > 0: color = C_GREEN
        elif change < 0: color = C_RED
        dtext(x + 150, y, color, str(new_param))