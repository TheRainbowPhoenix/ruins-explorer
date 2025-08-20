# cpgame/game_windows/window_shop_sell.py
from gint import *
from cpgame.game_windows.window_item_list import WindowItemList
from cpgame.systems.jrpg import JRPG

class WindowShopSell(WindowItemList):
    """This window displays the party's items for selling."""
    def make_item_list(self):
        if JRPG.objects:
            # Filter all party items by the current category
            self._data = [item for item in JRPG.objects.party.all_items() if self._item_matches_category(item)]

    def _item_matches_category(self, item) -> bool:
        if not item: return False
        if self._category == 'item' and item._category == 'items': return True
        if self._category == 'weapon' and item._category == 'weapons': return True
        if self._category == 'armor' and item._category == 'armors': return True
        return False

    def is_enabled(self, item) -> bool:
        """An item can be sold if it has a price greater than 0."""
        return item is not None and item.price > 0