# cpgame/game_windows/window_shop_number.py
from gint import *
from cpgame.game_windows.window_selectable import WindowSelectable

try:
    from typing import Optional
    from cpgame.engine.systems import InputManager
except: pass

class WindowShopNumber(WindowSelectable):
    """A window for inputting the quantity to buy or sell."""
    def __init__(self, x: int, y: int, width: int, height: int):
        super().__init__(x, y, width, height)
        self._item = None
        self._max = 1
        self._price = 0
        self._number = 1
        self.visible = False
        self.active = False

    def start(self, item, max_quantity, price):
        self._item = item
        self._max = max_quantity
        self._price = price
        self._number = 1
        self.visible = True
        self.activate()
        self.refresh()

    def handle_input(self, input_manager: Optional[InputManager]): 
        if not self.active: return
        if not input_manager: return
        
        last_number = self._number
        if input_manager.is_trigger('up'): self._number = min(self._number + 1, self._max)
        if input_manager.is_trigger('down'): self._number = max(self._number - 1, 1)
        if input_manager.is_trigger('right'): self._number = min(self._number + 10, self._max)
        if input_manager.is_trigger('left'): self._number = max(self._number - 10, 1)
        
        if self._number != last_number: self.refresh()

        if input_manager.is_trigger('confirm'): self.call_handler('ok', self._number)
        if input_manager.is_trigger('cancel'): self.call_handler('cancel')

    def draw(self):
        if not self.visible: return
        self._draw_skin()
        
        if not self._item: return

        # Draw item name
        dtext(self.x + self.padding, self.y + 4, C_BLACK, self._item.name)

        # Draw quantity
        quantity_text = "x {}".format(self._number)
        dtext(self.x + self.width // 2, self.y + 4, C_BLACK, quantity_text)
        
        # Draw total price
        total_price = str(self._price * self._number) + " G"
        price_width = len(total_price) * 8
        dtext(self.x + self.width - self.padding - price_width, self.y + 30, C_BLACK, total_price)