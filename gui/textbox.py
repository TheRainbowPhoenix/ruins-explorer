from .base import GUIElement
from .canvas import Canvas
from gint import C_BLACK, C_NONE

class TextBoxFlag:
    FlagDrawBox = 1 << 3
    FlagEditable = 1 << 8

class GUITextBox(GUIElement):
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        initial: str = None,
        max_length: int = 0,
        count_by_bytes: bool = False,
        flags: TextBoxFlag = TextBoxFlag.FlagDrawBox | TextBoxFlag.FlagEditable
    ):
        """
        Create a text box:
        - x, y: top-left in pixels
        - width: in pixels
        - initial: optional initial text
        - max_length: max chars (or bytes if count_by_bytes)
        - flags: draw box and/or editable
        """
        # height of one line
        height = Canvas.char_height
        super().__init__(x, y, x + width, y + height, event_id=None, flags=flags)

        self._text = initial or ""
        self.max_length = max_length
        self.count_by_bytes = count_by_bytes
        self.cursor_pos = len(self._text)

    def GetText(self) -> str:
        """Returns the current text."""
        return self._text

    def SetText(self, text: str):
        """Sets the text, enforcing max_length."""
        # enforce limit
        if self.max_length > 0:
            if self.count_by_bytes:
                b = text.encode('utf-8')[:self.max_length]
                text = b.decode('utf-8', errors='ignore')
            else:
                text = text[:self.max_length]
        self._text = text
        self.cursor_pos = len(self._text)

    def render(self, canvas: Canvas):
        # draw box
        if self.flags & TextBoxFlag.FlagDrawBox:
            canvas.draw_rect(self.bounds)
        # draw text
        canvas.draw_text(self._text, (self.left + 2, self.top + 1))
        # draw cursor
        if self.flags & TextBoxFlag.FlagEditable:
            cx = self.left + 2 + self.cursor_pos * Canvas.char_width
            cy1 = self.top + 1
            cy2 = cy1 + Canvas.char_height - 2
            canvas.draw_line((cx, cy1), (cx, cy2), C_BLACK)

    def handleEvent(self, ev) -> bool:
        """
        Handle key events:
        - BACKSPACE, LEFT, RIGHT, printable, ENTER to post event_id
        """
        if not (self.flags & TextBoxFlag.FlagEditable) or ev is None:
            return False

        if ev.type == "key":
            key = ev.key
            # backspace
            if key == "BACKSPACE" and self.cursor_pos > 0:
                self._text = self._text[:self.cursor_pos - 1] + self._text[self.cursor_pos:]
                self.cursor_pos -= 1
                return True
            # left arrow
            if key == "LEFT" and self.cursor_pos > 0:
                self.cursor_pos -= 1
                return True
            # right arrow
            if key == "RIGHT" and self.cursor_pos < len(self._text):
                self.cursor_pos += 1
                return True
            # enter/return
            if key in ("ENTER", "RETURN"):
                if self.event_id is not None:
                    canvas.post_event(self.event_id)
                return True
            # printable chars
            if len(key) == 1:
                new_text = self._text[:self.cursor_pos] + key + self._text[self.cursor_pos:]
                # enforce limit
                if self.max_length > 0:
                    if self.count_by_bytes:
                        if len(new_text.encode('utf-8')) > self.max_length:
                            return True
                    else:
                        if len(new_text) > self.max_length:
                            return True
                self._text = new_text
                self.cursor_pos += 1
                return True

        return False
