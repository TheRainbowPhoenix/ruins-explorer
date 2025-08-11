# gui/label.py

import gint
from .base import GUIElement, Widget
from .canvas import Canvas
from gint import C_BLACK, C_NONE
import gint

class Label(Widget):
    """A widget that displays a single line of text."""
    def __init__(self, x, y, text, text_color=gint.C_BLACK, bg_color=gint.C_NONE):
        # A simple approximation for width/height
        width = len(text) * 8 
        height = 12
        super().__init__(x, y, width, height)
        self.text = text
        self.text_color = text_color
        self.bg_color = bg_color

    def set_text(self, new_text):
        if self.text != new_text:
            self.text = new_text
            self.rect.right = self.rect.left + len(new_text) * 8 - 1 # Recalculate width
            self.set_needs_redraw()

    def on_draw(self):
        abs_pos = self.get_absolute_rect()
        gint.dtext_opt(
            abs_pos.left, abs_pos.top,
            self.text_color, self.bg_color,
            gint.DTEXT_LEFT, gint.DTEXT_TOP,
            self.text, -1
        )


class LabelFlag:
    FlagBackground = 1 << 0
    FlagSelectable = 1 << 15

class GUILabel(GUIElement):
    def __init__(
        self,
        x,
        y,
        text,
        flags = 0,
        text_color = C_BLACK,
        background_color = C_NONE,
        show_shadow = False,
        shadow_color = C_BLACK
    ):
        """
        x, y: top-left corner
        text: initial string
        flags: combination of LabelFlag
        text_color: color of the text
        background_color: only used if FlagBackground is set
        show_shadow/shadow_color: draw a 1px offset shadow
        """
        # Compute width/height from Canvas metrics
        width  = len(text) * Canvas.char_width
        height = Canvas.char_height

        super().__init__(x, y, x + width, y + height,
                         event_id=None, flags=flags)

        self.text             = text
        self.text_color       = text_color
        self.background_color = background_color
        self.show_shadow      = show_shadow
        self.shadow_color     = shadow_color

        # for selectable labels: this gets toggled by whatever focus logic you have
        self.selected = False

    def GetText(self) -> str:
        return self.text

    def SetText(self, text: str):
        self.text = text
        # Optionally, you could recompute self.bounds here if text length changes.

    def Refresh(self):
        # No-op: your dialog’s Refresh() will call render() on this element
        pass

    def Draw(self):
        fg = self.text_color
        bg = C_NONE
        if self.flags & LabelFlag.FlagBackground:
            bg = self.background_color

        if (self.flags & LabelFlag.FlagSelectable) and self.selected:
            fg, bg = bg, fg  # swap on selection

        # Optional shadow
        if self.show_shadow:
            gint.dtext_opt(self.left, self.top + 1, self.shadow_color, gint.C_NONE, gint.DTEXT_LEFT, gint.DTEXT_TOP, self.text, -1)
        #     canvas.draw_text(
        #         self.text,
        #         (self.left + 1, self.top + 1),
        #         fg=self.shadow_color,
        #         bg=C_NONE
        #     )
            

        # Draw the label text
        gint.dtext_opt(self.left, self.top, fg, bg, gint.DTEXT_LEFT, gint.DTEXT_TOP, self.text, -1)

    def render(self, canvas: Canvas):
        # Determine fg/bg based on flags + selected state
        fg = self.text_color
        bg = C_NONE
        if self.flags & LabelFlag.FlagBackground:
            bg = self.background_color

        if (self.flags & LabelFlag.FlagSelectable) and self.selected:
            fg, bg = bg, fg  # swap on selection

        # Optional shadow
        if self.show_shadow:
            canvas.draw_text(
                self.text,
                (self.left + 1, self.top + 1),
                fg=self.shadow_color,
                bg=C_NONE
            )

        # Draw the label text
        canvas.draw_text(
            self.text,
            (self.left, self.top),
            fg=fg,
            bg=bg
        )
