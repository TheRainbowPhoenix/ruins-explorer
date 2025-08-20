# cpgame/game_windows/window_shop_buy.py
from gint import *
from cpgame.game_windows.window_item_list import WindowItemList
from cpgame.systems.jrpg import JRPG

class WindowShopBuy(WindowItemList):
    """This window displays a list of buyable goods on the shop screen."""
    def __init__(self, x: int, y: int, width: int, height: int, goods: list):
        self._goods = goods
        self._data = []
        self._price = {}
        self._money = 0
        super().__init__(x, y, width, height)

    def set_money(self, money: int):
        self._money = money
        self.refresh()

    def item(self):
        if self.index < len(self._data) and self.index >= 0:
            return self._data[self.index]
        return None

    def make_item_list(self):
        self._data = []
        self._price = {}
        for goods_item in self._goods:
            item_type, item_id, _, price_override = goods_item
            
            data_proxy = None
            if JRPG.data:
                if item_type == 0: data_proxy = JRPG.data.items
                elif item_type == 1: data_proxy = JRPG.data.weapons
                elif item_type == 2: data_proxy = JRPG.data.armors
            
            if data_proxy:
                # Use a with block for safe, temporary loading
                with data_proxy.load(item_id) as item_data:
                    if item_data:
                        self._data.append(item_data)
                        self._price[item_data.name] = price_override if price_override > 0 else item_data.price

    def get_price(self, item) -> int:
        return self._price.get(item.name, 0)

    def is_enabled(self, item) -> bool:
        if not item: return False
        return self.get_price(item) <= self._money # and not JRPG.objects.party.is_max_items(item)

    def draw_item(self, index: int):
        item = self._data[index]
        if item:
            enabled = self.is_enabled(item)
            color = C_BLACK if enabled else C_DARK
            
            # Draw item name
            dtext(self.x + self.padding, self.y + self.padding + index * self.line_height, color, item.name)
            
            # Draw price
            price_text = str(self.get_price(item))
            text_width = len(price_text) * 8
            dtext(self.x + self.width - self.padding - text_width, self.y + self.padding + index * self.line_height, color, price_text)