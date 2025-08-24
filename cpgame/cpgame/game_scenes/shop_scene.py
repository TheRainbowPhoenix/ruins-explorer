# cpgame/game_scenes/shop_scene.py
import gint
from cpgame.game_scenes._scenes_base import SceneBase
from cpgame.systems.jrpg import JRPG
from cpgame.engine.logger import log

# --- Layout Constants ---
TOP_BAR_H = 30
GOLD_BAR_H = 30
LIST_Y = TOP_BAR_H + GOLD_BAR_H
INFO_PANEL_H = 80

C_YELLOW = 0b00000_111111_11111

_BG_COLOR = gint.C_RGB(30, 26, 13)
_BORDER_OUTER_COLOR = gint.C_RGB(18, 10, 2)
_BORDER_INNER_COLOR = gint.C_RGB(29, 22, 8)
_TEXT_COLOR = gint.C_RGB(5, 2, 0)
_TEXT_DISABLED_COLOR = gint.C_RGB(15, 13, 7) # A faded brown for disabled text
_GOLD_TEXT_COLOR = gint.C_RGB(31, 31, 20)   # A bright yellow for gold
_SELECT_COLOR = gint.C_RGB(25, 12, 5)
_SELECT_BG_COLOR = gint.C_RGB(31, 28, 20) # A light parchment color for selection

class SceneShop(SceneBase):
    """
    A lightweight, state-driven shop scene designed for low-memory environments.
    It manages all its UI states internally without separate window objects.
    """
    def __init__(self, game, **kwargs):
        super().__init__(game)
        self._goods = kwargs.get('goods', [])
        self._purchase_only = kwargs.get('purchase_only', False)
        
        # --- State Machine ---
        self._state = "COMMAND"  # COMMAND, BUY, SELL, QUANTITY
        self._active_list = []
        
        # --- UI State ---
        self._command_index = 0
        self._item_index = 0
        self._top_item_index = 0 # For scrolling
        self._quantity = 1
        
        # Layout
        self._top_bar_h = 30
        self._gold_bar_h = 30
        self._info_panel_h = 80
        self._list_y = self._top_bar_h + self._gold_bar_h
        self._list_height = gint.DHEIGHT - self._list_y - self._info_panel_h
        self._items_per_page = self._list_height // 24

    def create(self):
        log("ShopScene: Created.")
        self._prepare_buy_list()

    def update(self, dt):
        # self.input.update()
        
        # Route input based on the current state
        if self._state == "COMMAND":
            self.update_command_selection()
        elif self._state in ("BUY", "SELL"):
            self.update_item_selection()
        elif self._state in ("QUANTITY_BUY", "QUANTITY_SELL"):
            self.update_quantity_selection()
            
    def draw(self, frame_time_ms):
        gint.dclear(_BG_COLOR) # Use the main background color
        self.draw_top_bar()
        self.draw_gold_bar()
        self.draw_item_list()
        self.draw_info_panel()

        if self._state in ("QUANTITY_BUY", "QUANTITY_SELL"):
            self.draw_quantity_box()

    # --- State Update Methods ---

    def update_command_selection(self):
        if self.input.left: self._command_index = max(0, self._command_index - 1)
        if self.input.right: self._command_index = min(2, self._command_index + 1)
        
        if self.input.is_trigger('confirm'):
            if self._command_index == 0: # Buy
                self._state = "BUY"
                self._prepare_buy_list()
            elif self._command_index == 1 and not self._purchase_only: # Sell
                self._state = "SELL"
                self._prepare_sell_list()
            elif self._command_index == 2 or (self._command_index == 1 and self._purchase_only): # Exit
                if JRPG.game:
                    self.draw_loading_screen()
                    from cpgame.game_scenes.scene_map import SceneMap
                    JRPG.game.change_scene(SceneMap)

    def update_item_selection(self):
        if not self._active_list:
            if self.input.is_trigger('cancel'):
                self._state = "COMMAND"
            return

        if self.input.up: self._item_index = max(0, self._item_index - 1)
        if self.input.down: self._item_index = min(len(self._active_list) - 1, self._item_index + 1)

        # Page scrolling
        if self.input.is_trigger('page_up'): # Page Up
            self._item_index = max(0, self._item_index - self._items_per_page)
        if self.input.is_trigger('page_down'): # Page Down
            self._item_index = min(len(self._active_list) - 1, self._item_index + self._items_per_page)
            
        # Ensure cursor is visible
        if self._item_index < self._top_item_index:
            self._top_item_index = self._item_index
        if self._item_index >= self._top_item_index + self._items_per_page:
            self._top_item_index = self._item_index - self._items_per_page + 1

        if self.input.is_trigger('confirm'):
            item = self._active_list[self._item_index]
            can_afford = self._state == 'SELL' or (JRPG.objects and JRPG.objects.party.gold >= item.shop_price)
            if can_afford:
                self._state = "QUANTITY_BUY" if self._state == "BUY" else "QUANTITY_SELL"
                self._quantity = 1
        
        elif self.input.is_trigger('cancel'):
            self._state = "COMMAND"
            self._item_index = 0
            self._top_item_index = 0

    def update_quantity_selection(self):
        max_qty = self._get_max_quantity()
        
        if self.input.up: self._quantity = min(self._quantity + 1, max_qty)
        if self.input.down: self._quantity = max(self._quantity - 1, 1)

        if self.input.is_trigger('page_up'): # Page Up
            self._quantity = min(self._quantity + 10, max_qty)
        if self.input.is_trigger('page_down'): # Page Down
            self._quantity = max(self._quantity - 10, 1)

        if self.input.right: self._quantity = min(99, max_qty)
        if self.input.left: self._quantity = max_qty

        if self.input.is_trigger('confirm'):
            self._execute_transaction()
            self._state = "BUY" if self._state == "QUANTITY_BUY" else "SELL" # Go back to list
            self._prepare_buy_list() if self._state == "BUY" else self._prepare_sell_list()
        elif self.input.is_trigger('cancel'):
            self._state = "BUY" if self._state == "QUANTITY_BUY" else "SELL"

    # --- Drawing Methods ---

    def draw_top_bar(self):
        gint.drect(0, 0, gint.DWIDTH - 1, TOP_BAR_H - 1, _BG_COLOR)
        gint.drect_border(0,0,gint.DWIDTH-1, TOP_BAR_H-1, gint.C_NONE, 1, _BORDER_OUTER_COLOR)
        
        commands = ["Buy", "Sell", "Exit"]
        if self._purchase_only: commands[1] = "---"
        
        for i, cmd in enumerate(commands):
            x = (gint.DWIDTH // 3) * i
            color = _TEXT_COLOR
            if self._state == "COMMAND" and i == self._command_index:
                gint.drect(x, 0, x + (gint.DWIDTH // 3) -1, TOP_BAR_H - 1, _SELECT_BG_COLOR)
                gint.drect_border(x,0,x+(gint.DWIDTH//3)-1, TOP_BAR_H-1, gint.C_NONE, 1, _SELECT_COLOR)
            gint.dtext_opt(x + (gint.DWIDTH // 6), TOP_BAR_H // 2, color, gint.C_NONE, gint.DTEXT_CENTER, gint.DTEXT_MIDDLE, cmd, -1)

    def draw_gold_bar(self):
        y = TOP_BAR_H
        gint.drect(0, y, gint.DWIDTH - 1, y + GOLD_BAR_H - 1, _BORDER_OUTER_COLOR)
        if JRPG.objects:
            gold_text = "Gold: {} G".format(JRPG.objects.party.gold)
            gint.dtext_opt(gint.DWIDTH - 10, y + GOLD_BAR_H // 2, _GOLD_TEXT_COLOR, gint.C_NONE, gint.DTEXT_RIGHT, gint.DTEXT_MIDDLE, gold_text, -1)

    def draw_item_list(self):
        if self._state not in ("BUY", "SELL"): return
        
        for i in range(self._items_per_page):
            index = self._top_item_index + i
            if index >= len(self._active_list): break
            
            item = self._active_list[index]
            y = LIST_Y + i * 24
            
            if index == self._item_index:
                gint.drect(0, y, gint.DWIDTH - 1, y + 23, _SELECT_BG_COLOR)
                gint.drect_border(0,y,gint.DWIDTH-1, y+23, gint.C_NONE, 1, _SELECT_COLOR)
            
            can_afford = True
            name = item.name
            if self._state == 'BUY':
                price = item.shop_price
                can_afford = (JRPG.objects and JRPG.objects.party.gold >= price)
            else: # SELL
                price = int(item.price * 0.8)
                quantity = JRPG.objects.party.item_number(item) if JRPG.objects else ""

                name += " ({})".format(quantity) # TODO: add inventory item quantity here

            # NEW: Set color based on affordability
            item_color = _TEXT_COLOR if can_afford else _TEXT_DISABLED_COLOR
            price_color = _TEXT_COLOR if can_afford else _TEXT_DISABLED_COLOR
            
            gint.dtext(10, y + 4, item_color, name)
            
            price_text = str(price) + " G"
            gint.dtext_opt(gint.DWIDTH - 10, y + 12, price_color, gint.C_NONE, gint.DTEXT_RIGHT, gint.DTEXT_MIDDLE, price_text, -1)

    def draw_info_panel(self):
        y = gint.DHEIGHT - INFO_PANEL_H
        gint.drect(0, y, gint.DWIDTH - 1, gint.DHEIGHT - 1, _BG_COLOR)
        gint.drect_border(0, y, gint.DWIDTH-1, gint.DHEIGHT-1, gint.C_NONE, 1, _BORDER_OUTER_COLOR)
        gint.drect_border(1, y+1, gint.DWIDTH-2, gint.DHEIGHT-2, gint.C_NONE, 1, _BORDER_INNER_COLOR)
        
        if self._state in ("BUY", "SELL") and self._active_list:
            item = self._active_list[self._item_index]
            gint.dtext(10, y + 8, _TEXT_COLOR, item.description)

    def draw_quantity_box(self):
        w, h = 200, 100
        x = (gint.DWIDTH - w) // 2
        y = (gint.DHEIGHT - h) // 2
        gint.drect(x, y, x + w - 1, y + h - 1, _BG_COLOR)
        gint.drect_border(x, y, x + w - 1, y + h - 1, gint.C_NONE, 1, _BORDER_OUTER_COLOR)
        gint.drect_border(x+1, y+1, x + w - 2, y + h - 2, gint.C_NONE, 1, _BORDER_INNER_COLOR)

        item = self._active_list[self._item_index]
        gint.dtext_opt(x + w//2, y + 10, _TEXT_COLOR, gint.C_NONE, gint.DTEXT_CENTER, gint.DTEXT_TOP, item.name, -1)
        gint.dtext_opt(x + w//2, y + 40, _TEXT_COLOR, gint.C_NONE, gint.DTEXT_CENTER, gint.DTEXT_TOP, "Quantity: {}".format(self._quantity), -1)

    # --- Logic Helpers ---

    def _prepare_buy_list(self):
        self._active_list = []
        if not JRPG.data:
            return

        for item_type, item_id, price_type, price_override, purchase_only in self._goods:
            proxy = [JRPG.data.items, JRPG.data.weapons, JRPG.data.armors][item_type]
            with proxy.load(item_id) as item_data:
                if item_data:
                    # Store price directly on a temporary attribute for convenience
                    item_data.shop_price = price_override if price_override > 0 else item_data.get('price', 0)
                    self._active_list.append(item_data)
        self._item_index = self._top_item_index = 0

    def _prepare_sell_list(self):
        if not JRPG.objects:
            return
        self._active_list = [item for item in JRPG.objects.party.all_items() if item and item.get('price', 0) > 0]
        self._item_index = self._top_item_index = 0

    def _get_max_quantity(self) -> int:
        if not JRPG.objects:
            return 1
        
        item = self._active_list[self._item_index]
        if self._state == 'QUANTITY_BUY':
            price = item.shop_price
            # If price is 0, they can take 99. Otherwise, calculate based on gold.
            return min(JRPG.objects.party.gold // price if price > 0 else 99, 99)
        elif self._state == 'QUANTITY_SELL': # SELL
            return JRPG.objects.party.item_number(item)
        return 0
            
    def _execute_transaction(self):
        if not JRPG.objects:
            return

        item = self._active_list[self._item_index]
        if self._state == 'QUANTITY_BUY':
            price = item.shop_price
            JRPG.objects.party.lose_gold(price * self._quantity)
            JRPG.objects.party.gain_item(item, self._quantity)
        elif self._state == "QUANTITY_SELL": # SELL
            price = item.price * 0.8
            JRPG.objects.party.gain_gold(price * self._quantity)
            JRPG.objects.party.gain_item(item, -self._quantity)
