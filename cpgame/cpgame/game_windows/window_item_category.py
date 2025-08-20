# cpgame/game_windows/window_item_category.py
from cpgame.game_windows.window_horz_command import WindowHorzCommand

class WindowItemCategory(WindowHorzCommand):
    """Window for selecting item categories (Items, Weapons, Armor)."""
    def __init__(self, x, y, width, height):
        self._item_window = None
        super().__init__(x, y, width, height)
    
    @property
    def col_max(self) -> int:
        """Number of columns in grid layout."""
        return 3 # We'll do Item, Weapon, Armor for the shop

    def set_item_window(self, window):
        self._item_window = window

    def make_command_list(self):
        self.add_command("Items", 'item')
        self.add_command("Weapons", 'weapon')
        self.add_command("Armor", 'armor')

    def update(self):
        super().update()
        if self._item_window:
            self._item_window.set_category(self.current_symbol())