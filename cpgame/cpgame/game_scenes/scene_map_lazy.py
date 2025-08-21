# cpgame/game_scenes/shop_scene.py
from gint import *
from cpgame.game_scenes._scenes_base import SceneBase
from cpgame.systems.jrpg import JRPG

# Import window classes one by one to be explicit
from cpgame.game_windows.window_gold import WindowGold
from cpgame.game_windows.window_shop_command import WindowShopCommand
from cpgame.game_windows.window_shop_buy import WindowShopBuy
from cpgame.game_windows.window_shop_sell import WindowShopSell
from cpgame.game_windows.window_shop_number import WindowShopNumber
from cpgame.game_windows.window_shop_status import WindowShopStatus
from cpgame.game_windows.window_item_category import WindowItemCategory
from cpgame.game_windows.window_help import WindowHelp
from cpgame.game_windows.window_base import WindowBase

class SceneShop(SceneBase):
    def __init__(self, game, goods, purchase_only):
        super().__init__(game)
        self._goods = goods
        self._purchase_only = purchase_only
        self._item = None

    def create(self):
        """Creates only the essential, always-visible windows."""
        self.help_window = WindowHelp()
        self.gold_window = WindowGold(DWIDTH - 160, self.help_window.height)
        self.command_window = WindowShopCommand(0, self.help_window.height, DWIDTH - 160, self._purchase_only)
        
        # This dummy window is just a background for the lists, so it's okay to create.
        y = self.command_window.y + self.command_window.height
        h = DHEIGHT - y
        self.dummy_window = Window_Base(0, y, DWIDTH, h)
        
        self._windows = [self.help_window, self.gold_window, self.command_window, self.dummy_window]
        
        # --- Lazy-loaded window instances ---
        self.buy_window = None
        self.sell_window = None
        self.status_window = None
        self.number_window = None
        self.category_window = None
        
        # Setup handlers for the initially visible window
        self.command_window.set_handler('buy', self.command_buy)
        self.command_window.set_handler('sell', self.command_sell)
        self.command_window.set_handler('cancel', self.pop_scene)

        self._active_window = self.command_window
        self.command_window.activate()

    # --- Command Handlers ---
    def pop_scene(self): self.game.pop_scene()

    def command_buy(self):
        self.command_window.deactivate()
        self.dummy_window.visible = False
        
        # Create windows only when needed
        if not self.buy_window:
            y = self.dummy_window.y
            h = self.dummy_window.height
            self.buy_window = WindowShopBuy(0, y, DWIDTH // 2 + 20, h, self._goods)
            self.buy_window.set_handler('ok', self.on_buy_ok)
            self.buy_window.set_handler('cancel', self.on_buy_cancel)
            self._windows.append(self.buy_window)

        if not self.status_window:
            x = self.buy_window.width
            y = self.dummy_window.y
            w = DWIDTH - x
            h = self.dummy_window.height
            self.status_window = WindowShopStatus(x, y, w, h)
            self._windows.append(self.status_window)
            self.buy_window.status_window = self.status_window # Link them

        self.buy_window.set_money(JRPG.objects.party.gold)
        self.buy_window.visible = True
        self.status_window.visible = True
        self._active_window = self.buy_window
        self.buy_window.activate()

    def on_buy_cancel(self):
        self._active_window = self.command_window
        if self.buy_window: self.buy_window.visible = False; self.buy_window.deactivate()
        if self.status_window: self.status_window.visible = False
        self.dummy_window.visible = True
        self.command_window.activate()

    def on_buy_ok(self):
        self._item = self.buy_window.item()
        
        if not self.number_window:
            self.number_window = WindowShopNumber(0, 0, 300, 80)
            self.number_window.set_handler('ok', self.on_number_ok)
            self.number_window.set_handler('cancel', self.on_number_cancel)
            self._windows.append(self.number_window)
            
        self.buy_window.deactivate()
        
        price = self.buy_window.get_price(self._item)
        max_buy = JRPG.objects.party.gold // price if price > 0 else 99
        self.number_window.start(self._item, max_buy, price)
        self._active_window = self.number_window

    def on_number_ok(self, number):
        # ... (logic is the same)
        self.end_number_input()
        
    def on_number_cancel(self):
        self.end_number_input()
        
    def end_number_input(self):
        if self.number_window:
            self.number_window.visible = False
            self.number_window.deactivate()
            
        # Return to the previous screen (buy or sell)
        if self.command_window.current_symbol() == 'buy':
            self.buy_window.visible = True
            self.buy_window.activate()
            self._active_window = self.buy_window
        else: # Selling
            # Reactivate sell screen logic...
            pass

    # TODO: Implement `command_sell` and its handlers (`on_sell_ok`, etc.) using the same lazy-loading pattern