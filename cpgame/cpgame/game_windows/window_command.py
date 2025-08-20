# cpgame/game_windows/window_command.py
from gint import dtext, C_BLACK, C_DARK
from cpgame.game_windows.window_selectable import WindowSelectable


class WindowCommand(WindowSelectable):
    """
    A window for displaying a list of commands.
    Subclasses should override make_command_list() to populate commands.
    """

    def __init__(self, x, y, width=None, height=None):
        self._list = []
        self.clear_command_list()
        self.make_command_list()
        
        # Use default width if not provided
        w = width or self.window_width()
        h = height or self.window_height()

        super().__init__(x, y, w, h)
        self.refresh()
        self.index = 0
        self.activate()

    def window_width(self) -> int:
        """Return the default window width."""
        return 160

    def window_height(self) -> int:
        """Return the window height based on visible lines."""
        return self.fitting_height(self.visible_line_number())

    def visible_line_number(self) -> int:
        """Return the number of visible lines (same as item count)."""
        return self.item_max

    @property
    def item_max(self) -> int:
        """Return the number of commands in the list."""
        return len(self._list)

    def clear_command_list(self):
        """Clear all commands from the list."""
        self._list = []

    def make_command_list(self):
        """
        Populate the command list.
        Should be overridden by subclasses.
        """
        pass

    def add_command(self, name: str, symbol: str, enabled: bool = True, ext=None):
        """
        Add a command to the list.

        :param name: Display name of the command
        :param symbol: Symbol identifying the command
        :param enabled: Whether the command is selectable
        :param ext: Optional extended data
        """
        self._list.append({
            'name': name,
            'symbol': symbol,
            'enabled': enabled,
            'ext': ext
        })

    def command_name(self, index: int) -> str:
        """Get the name of the command at the given index."""
        return self._list[index]['name']

    def command_enabled(self, index: int) -> bool:
        """Check if the command at the given index is enabled."""
        return self._list[index]['enabled']

    def current_data(self):
        """Get the data of the currently selected command."""
        if self.index < 0 or self.index >= len(self._list):
            return None
        return self._list[self.index]

    def current_item_enabled(self) -> bool:
        """Check if the currently selected command is enabled."""
        data = self.current_data()
        return data['enabled'] if data else False

    def current_symbol(self):
        """Get the symbol of the currently selected command."""
        data = self.current_data()
        return data['symbol'] if data else None

    def current_ext(self):
        """Get the extended data of the currently selected command."""
        data = self.current_data()
        return data['ext'] if data else None

    def select_symbol(self, symbol):
        """Move cursor to the command with the specified symbol."""
        for i, item in enumerate(self._list):
            if item['symbol'] == symbol:
                self.index = i
                break

    def select_ext(self, ext):
        """Move cursor to the command with the specified extended data."""
        for i, item in enumerate(self._list):
            if item['ext'] == ext:
                self.index = i
                break

    def draw_item(self, index: int):
        """Draw the command at the specified index."""
        item = self._list[index]
        rect = self.item_rect_for_text(index)
        color = C_BLACK if item['enabled'] else C_DARK
        if not item['enabled']:
            # Optionally dim disabled items
            pass
        dtext(rect.x, rect.y, color, item['name'])

    def alignment(self) -> int:
        """Return text alignment (0 = left)."""
        return 0

    def ok_enabled(self) -> bool:
        """Return whether OK input is allowed."""
        return True

    def call_ok_handler(self):
        """Call the appropriate handler when OK is pressed."""
        symbol = self.current_symbol()
        
        if symbol and self.handle(symbol):
            self.call_handler(symbol)
        elif self.handle('ok'):
            super().call_ok_handler()
        else:
            self.activate()

    def refresh(self):
        """Refresh the command window by rebuilding content."""
        self.clear_command_list()
        self.make_command_list()
        self.create_contents()  # Rebuilds the surface or text buffer
        super().refresh()  # Call parent refresh if needed