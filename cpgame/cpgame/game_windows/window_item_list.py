# cpgame/game_windows/window_item_list.py
from cpgame.game_windows.window_selectable import WindowSelectable

class WindowItemList(WindowSelectable):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self._data = []
        self._category = 'item'

    def set_category(self, category: str):
        if self._category != category:
            self._category = category
            self.refresh()
    
    @property
    def item_max(self) -> int:
        return len(self._data)
    
    def item(self):
        if self.index < len(self._data) and self.index >= 0:
            return self._data[self.index]
        return None

    # Subclasses will override make_item_list and draw_item
    def make_item_list(self): self._data = []
    def refresh(self):
        self.make_item_list()
        super().refresh()