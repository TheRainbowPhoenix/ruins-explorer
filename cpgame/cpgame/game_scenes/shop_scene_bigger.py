# cpgame/game_scenes/shop_scene.py
from gint import *
from cpgame.systems.jrpg import JRPG
from cpgame.engine.logger import log
from cpgame.game_scenes._scenes_base import SceneMenuBase

# Import all the necessary window classes
from cpgame.game_windows.window_base import WindowBase
from cpgame.game_windows.window_gold import WindowGold
from cpgame.game_windows.window_shop_command import WindowShopCommand
from cpgame.game_windows.window_shop_buy import WindowShopBuy
from cpgame.game_windows.window_shop_sell import WindowShopSell
from cpgame.game_windows.window_shop_number import WindowShopNumber
from cpgame.game_windows.window_shop_status import WindowShopStatus
from cpgame.game_windows.window_item_category import WindowItemCategory
from cpgame.game_windows.window_help import WindowHelp

class SceneShop(SceneMenuBase): # 
    def __init__(self, game, goods, purchase_only):
        super().__init__(game)
        self._goods = goods
        self._purchase_only = purchase_only
        self._active_window = None
        self._item = None # The currently selected item

    def create(self):
        """Creates and lays out all windows for the shop."""
        self.create_help_window()
        self.create_gold_window()
        self.create_command_window()
        self.create_dummy_window() # Background for lists
        self.create_buy_window()
        self.create_status_window()
        self.create_number_window()
        self.create_category_window()
        self.create_sell_window()
        
        # Assemble window list for easy updates/drawing
        self._windows = [
            self.help_window, self.gold_window, self.command_window, self.dummy_window,
            self.buy_window, self.sell_window, self.status_window, self.number_window,
            self.category_window
        ]
        
        self._active_window = self.command_window
        self.command_window.activate()
        for window in self._windows:
            window.activate()

    def update(self, dt):
        super().update(dt) # This calls self.input.update() and updates the active window
        
        # First, poll the input state for this frame
        self.input.update()


        # Update all windows
        for window in self._windows:
            window.update()
        
        # if self.input.shift or self.input.exit: # Allow exiting with SHIFT key
        #     self.pop_scene()
        
        # --- INPUT & LOGIC PHASE ---
        if self._active_window:
            # If a modal window is active, it gets all input
            self._active_window.handle_input(self.input) # update ? handle_input ?
            # Add touch handling placeholder
            # touch = get_touch_event() 
            # if touch: self._active_window.handle_touch(touch.x, touch.y)

            return None

        return None

    # --- Window Creation Methods ---

    def create_help_window(self):
        self.help_window = WindowHelp()

    def create_gold_window(self):
        self.gold_window = WindowGold(DWIDTH - 160, self.help_window.height)

    def create_command_window(self):
        width = DWIDTH - self.gold_window.width
        self.command_window = WindowShopCommand(0, self.help_window.height, width, self._purchase_only)
        self.command_window.set_handler('buy', self.command_buy)
        self.command_window.set_handler('sell', self.command_sell)
        self.command_window.set_handler('cancel', self.pop_scene)

    def create_dummy_window(self):
        y = self.command_window.y + self.command_window.height
        h = DHEIGHT - y
        self.dummy_window = WindowBase(0, y, DWIDTH, h)

    def create_buy_window(self):
        y = self.dummy_window.y
        h = self.dummy_window.height
        self.buy_window = WindowShopBuy(0, y, DWIDTH // 2 + 20, h, self._goods)
        self.buy_window.visible = False
        self.buy_window.set_handler('ok', self.on_buy_ok)
        self.buy_window.set_handler('cancel', self.on_buy_cancel)
    
    def create_status_window(self):
        x = self.buy_window.width
        y = self.dummy_window.y
        w = DWIDTH - x
        h = self.dummy_window.height
        self.status_window = WindowShopStatus(x, y, w, h)
        # Link windows
        # self.buy_window.status_window = self.status_window

    def create_number_window(self):
        # This window is centered, so x,y are less important here
        self.number_window = WindowShopNumber(0, 0, 300, 80)
        self.number_window.set_handler('ok', self.on_number_ok)
        self.number_window.set_handler('cancel', self.on_number_cancel)

    def create_category_window(self):
        y = self.dummy_window.y
        self.category_window = WindowItemCategory(0, y, DWIDTH, 40)
        self.category_window.visible = False
        self.category_window.set_handler('ok', self.on_category_ok)
        self.category_window.set_handler('cancel', self.on_category_cancel)

    def create_sell_window(self):
        y = self.category_window.y + self.category_window.height
        h = DHEIGHT - y
        self.sell_window = WindowShopSell(0, y, DWIDTH, h)
        self.sell_window.visible = False
        self.category_window.set_item_window(self.sell_window) # Link windows
        self.sell_window.set_handler('ok', self.on_sell_ok)
        self.sell_window.set_handler('cancel', self.on_sell_cancel)

    # --- Command Handlers ---

    def pop_scene(self):
        if JRPG.game:
            self.draw_loading_screen()
            
            from cpgame.game_scenes.scene_map import SceneMap
            JRPG.game.change_scene(SceneMap)
        # self.game.pop_scene()

    def command_buy(self):
        self.command_window.deactivate()
        self.dummy_window.visible = False
        self.buy_window.set_money(JRPG.objects.party.gold if JRPG.objects else 1)
        self.buy_window.visible = True
        self.status_window.visible = True
        self._active_window = self.buy_window
        self.buy_window.activate()

    def command_sell(self):
        self.command_window.deactivate()
        self.dummy_window.visible = False
        self.category_window.visible = True
        self._active_window = self.category_window
        self.category_window.activate()

    def on_buy_cancel(self):
        self._active_window = self.command_window
        self.buy_window.deactivate()
        self.buy_window.visible = False
        self.status_window.visible = False
        self.dummy_window.visible = True
        self.command_window.activate()
        
    def on_category_ok(self):
        self._active_window = self.sell_window
        self.category_window.deactivate()
        self.sell_window.visible = True
        self.sell_window.activate()

    def on_category_cancel(self):
        self._active_window = self.command_window
        self.category_window.deactivate()
        self.category_window.visible = False
        self.dummy_window.visible = True
        self.command_window.activate()

    def on_buy_ok(self):
        self._item = self.buy_window.item()
        self.buy_window.deactivate()
        self.buy_window.visible = False
        self.status_window.visible = False
        
        price = self.buy_window.get_price(self._item)
        max_buy = (JRPG.objects.party.gold if JRPG.objects else 1) // price if price > 0 else 99
        self.number_window.start(self._item, max_buy, price)
        self._active_window = self.number_window

    def on_sell_ok(self):
        self._item = self.sell_window.item()
        self.category_window.deactivate()
        self.sell_window.deactivate()
        self.sell_window.visible = False

        if self._item and JRPG.objects:
            price = self._item.price // 2 # Sell price is half
            max_sell = JRPG.objects.party.item_number(self._item)
            self.number_window.start(self._item, max_sell, price)
            self._active_window = self.number_window

    def on_sell_cancel(self):
        self._active_window = self.category_window
        self.sell_window.deactivate()
        self.sell_window.visible = False
        self.category_window.activate()

    def on_number_ok(self, number):
        # Check if we are buying or selling
        if JRPG.objects:
            if self.command_window.current_symbol() == 'buy':
                JRPG.objects.party.lose_gold(self.buy_window.get_price(self._item) * number)
                if self._item: JRPG.objects.party.gain_item(self._item, number)
            else: # Selling
                JRPG.objects.party.gain_item(self._item, -number) # a.k.a. lose_item
                if self._item: JRPG.objects.party.gain_gold((self._item.price // 2) * number)

        self.gold_window.refresh()
        self.end_number_input()
        
    def on_number_cancel(self):
        self.end_number_input()
        
    def end_number_input(self):
        self.number_window.visible = False
        self.number_window.deactivate()
        # Return to the previous screen (buy or sell)
        if self.command_window.current_symbol() == 'buy':
            self.command_buy() # Reactivate buy screen
        else:
            self.on_category_ok() # Reactivate sell screen