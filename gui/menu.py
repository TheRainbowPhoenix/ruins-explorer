import gint
from .base import Widget, GUIEvent
from .window import Window
from .rect import Rect

C_LIGHT = 0xD69A
C_DARK = 0xAD55

class MenuItem(Widget):
    """An item within a menu. Can have a submenu."""
    def __init__(self, text, event_id=None, submenu=None):
        height = 14
        width = len(text) * 8 + 16 # Add padding
        super().__init__(0, 0, width, height)
        self.text = text
        self.event_id = event_id
        self.submenu = submenu
        if self.submenu:
            self.submenu.parent = self # For event propagation
        self.is_hovered = False

    def on_event(self, event):
        abs_rect = self.get_absolute_rect()
        
        if event.type == "touch_drag" or event.type == "touch_down":
             # Simple hover detection
            is_now_hovered = abs_rect.contains(event.pos[0], event.pos[1])
            if is_now_hovered != self.is_hovered:
                self.is_hovered = is_now_hovered
                self.set_needs_redraw()

        if event.type == "touch_up" and self.is_hovered:
            if self.event_id:
                # Fire a click event to be caught by the application
                click_event = GUIEvent("menu_click", self, item_id=self.event_id)
                # Propagate up to the application root
                ancestor = self
                while ancestor.parent:
                    ancestor = ancestor.parent
                ancestor.handle_event(click_event)
            
            # Close all menus after a click
            if self.parent and isinstance(self.parent.parent, Menu):
                self.parent.parent.hide()
            
            return True
        return False

    def on_draw(self):
        abs_rect = self.get_absolute_rect()
        bg = gint.C_BLUE if self.is_hovered else gint.C_WHITE
        fg = gint.C_WHITE if self.is_hovered else gint.C_BLACK
        
        gint.drect(abs_rect.left, abs_rect.top, abs_rect.right, abs_rect.bottom, bg)
        gint.dtext(abs_rect.left + 4, abs_rect.top + 2, fg, self.text)
        if self.submenu:
            gint.dtext(abs_rect.right - 10, abs_rect.top + 2, fg, ">")


class Menu(Window):
    """A popup menu that displays a list of MenuItems."""
    def __init__(self, title=""):
        # Dimensions will be calculated based on content
        super().__init__(0, 0, 1, 1, title)
        self.visible = False
        self.items = []

    def add_item(self, item: MenuItem):
        self.items.append(item)
        self.content.add_child(item)
        self._recalculate_size()

    def _recalculate_size(self):
        max_width = 0
        total_height = 14 # For title bar
        for item in self.items:
            if item.rect.width > max_width:
                max_width = item.rect.width
        total_height += sum(item.rect.height + self.content.padding for item in self.items)
        
        self.rect.right = self.rect.left + max_width + 4
        self.rect.bottom = self.rect.top + total_height
        self.content.rect.right = self.rect.width -1
        self.content.rect.bottom = self.rect.height -1
        self.content.do_layout()
        
    def show(self, x, y):
        self.rect.move_to(x, y)
        self.visible = True
        self.set_needs_redraw()
    
    def hide(self):
        self.visible = False
        # Hide all submenus as well
        for item in self.items:
            item.is_hovered = False
            if item.submenu and item.submenu.visible:
                item.submenu.hide()
        
        # Important: this needs to redraw the parent area
        if self.parent:
            self.parent.set_needs_redraw()


class MenuBar(Widget):
    """A horizontal bar at the top of the screen for menus."""
    def __init__(self, x, y, width):
        super().__init__(x, y, width, 15)
        self.menus = {} # text -> Menu
        self.active_menu_button = None

    def add_menu(self, text, menu: Menu):
        self.menus[text] = menu
        menu.parent = self # Set parent for event bubbling
        self.set_needs_redraw()

    def on_event(self, event):
        if event.type == "touch_down":
            abs_rect = self.get_absolute_rect()
            if abs_rect.contains(event.pos[0], event.pos[1]):
                x, y = event.pos
                
                # Find which menu title was clicked
                current_x = abs_rect.left + 2
                for text, menu in self.menus.items():
                    text_width = len(text) * 8 + 8
                    if current_x <= x < current_x + text_width:
                        # Hide any other active menu
                        if self.active_menu_button and self.active_menu_button is not menu:
                            self.active_menu_button.hide()
                        
                        # Toggle the clicked menu
                        if menu.visible:
                            menu.hide()
                            self.active_menu_button = None
                        else:
                            menu.show(current_x, abs_rect.bottom)
                            self.active_menu_button = menu
                        
                        return True
                    current_x += text_width

        # If a click happens outside the menu system, close the active menu
        if event.type == "touch_down" and self.active_menu_button:
            # Check if touch is inside the active menu tree
            in_menu_tree = False
            active_menu = self.active_menu_button
            while active_menu:
                if active_menu.get_absolute_rect().contains(event.pos[0], event.pos[1]):
                    in_menu_tree = True
                    break
                # Simple check for one level of submenu
                found_sub = False
                for item in active_menu.items:
                    if item.submenu and item.submenu.visible:
                        active_menu = item.submenu
                        found_sub = True
                        break
                if not found_sub:
                    active_menu = None
            
            if not in_menu_tree and not self.get_absolute_rect().contains(event.pos[0], event.pos[1]):
                self.active_menu_button.hide()
                self.active_menu_button = None
        
        return False # Don't block events for things underneath

    def on_draw(self):
        abs_rect = self.get_absolute_rect()
        gint.drect(abs_rect.left, abs_rect.top, abs_rect.right, abs_rect.bottom, C_LIGHT)
        
        current_x = abs_rect.left + 2
        for text, menu in self.menus.items():
            text_width = len(text) * 8 + 8
            is_active = menu.visible
            
            if is_active:
                gint.drect(current_x, abs_rect.top, current_x + text_width -1, abs_rect.bottom, C_DARK)
                gint.dtext(current_x + 4, abs_rect.top + 2, gint.C_WHITE, text)
            else:
                gint.dtext(current_x + 4, abs_rect.top + 2, gint.C_BLACK, text)

            current_x += text_width