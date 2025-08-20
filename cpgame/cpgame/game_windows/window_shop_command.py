# cpgame/game_windows/window_shop_command.py
from cpgame.game_windows.window_horz_command import WindowHorzCommand

class WindowShopCommand(WindowHorzCommand):
    """The window for selecting Buy, Sell, or Cancel in a shop."""
    def __init__(self, x: int, y: int, width: int, purchase_only: bool):
        self._purchase_only = purchase_only
        self.ox = 0
        super().__init__(x, y, width, 40)

    @property
    def col_max(self) -> int:
        """Number of columns in grid layout."""
        return 3

    def make_command_list(self):
        self.add_command("Buy", 'buy')
        self.add_command("Sell", 'sell', not self._purchase_only)
        self.add_command("Cancel", 'cancel')