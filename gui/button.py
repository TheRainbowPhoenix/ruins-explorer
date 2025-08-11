from .base import GUIElement, Widget, GUIEvent
import gint
from ._res import button as res_button
from .rect import Rect

C_LIGHT = 0xD69A
C_DARK = 0xAD55

class ButtonFlag:
    Enabled = 1 << 15

class Button(Widget):
    """A standard clickable button."""
    def __init__(self, x, y, width, height, text, event_id=None):
        super().__init__(x, y, width, height)
        self.text = text
        self.event_id = event_id
        self.is_pressed = False

    def on_event(self, event):
        abs_rect = self.get_absolute_rect()

        # if a touch operation ends, this button should not be pressed.
        if event.type == "touch_up":
            if self.is_pressed:
                self.is_pressed = False
                self.set_needs_redraw()
        
        if event.source is not self:
            return False
        
         # Handle the actual press and click logic
        if event.type == "touch_down":
            self.is_pressed = True
            self.set_needs_redraw()
            # Consume the event so no other widget underneath gets it.
            return True

        if event.type == "touch_up":
            # We already reset the visual state above. Now, fire the click event.
            # The click event is only fired if the touch_up happens inside the button.
            click_event = GUIEvent("click", self, button_id=self.event_id)
            
            # Propagate the 'click' event from the top-level widget.
            ancestor = self
            while ancestor.parent:
                ancestor = ancestor.parent
            ancestor.handle_event(click_event)
            
            # Consume the event.
            return True

        return False

    def on_draw(self):
        abs_rect = self.get_absolute_rect()
        
        # Determine colors based on state
        bg_color = C_DARK if self.is_pressed else C_LIGHT
        text_color = gint.C_WHITE if self.is_pressed else gint.C_BLACK
        border_color = gint.C_BLACK

        # Draw the button
        gint.drect(abs_rect.left, abs_rect.top, abs_rect.right, abs_rect.bottom, bg_color)
        gint.drect_border(abs_rect.left, abs_rect.top, abs_rect.right, abs_rect.bottom, 
                          gint.C_NONE, 1, border_color)
        
        # Center the text
        text_x = abs_rect.left + (abs_rect.width - len(self.text) * 8) // 2
        text_y = abs_rect.top + (abs_rect.height - 12) // 2
        
        gint.dtext(text_x, text_y, text_color, self.text)


class GUIButton(GUIElement):
    def __init__(self, left, top, right, bottom, text, event_id, flags=ButtonFlag.Enabled):
        super().__init__(left, top, right, bottom, event_id, flags)
        self.text = text
        self.pressed = False
    
    def Draw(self):
        resX = 13 if self.pressed else 0

        # draw header background
        xOffset = 5
        yOffset = 11

        gint.drect(
            self.left+xOffset, self.top+yOffset,
            self.right-xOffset, self.top +yOffset+ 16,
            gint.C_RGB(13,13,13)
        )

        gint.dsubimage(self.left, self.top, res_button, resX, 0, 6, 10)
        
        for x in range(self.left + xOffset, self.right-xOffset):
            gint.dsubimage(x, self.top, res_button, resX+5, 0, 1, 10)

        gint.dsubimage(self.right-xOffset, self.top, res_button, resX+6, 0, 7, 10)
        

        # fill body background
        gint.drect(
            self.left + 5,
            self.top + 9,
            self.right - 5,
            self.bottom - 5,
            gint.C_RGB(11, 27, 31) if self.pressed else gint.C_WHITE
        )

        gint.dtext_opt(
            self.left + 12, self.top + 8,
            gint.C_BLACK,
            gint.C_NONE,
            gint.DTEXT_LEFT, gint.DTEXT_TOP,
            self.text,
            -1
        )

        yOffset = 9
        for y in range(self.top + yOffset, self.bottom-5):
            gint.dsubimage(self.left, y, res_button, resX, 26, 6, 1)
            gint.dsubimage(self.right - 5, y, res_button, resX+6, 26, 6, 1)

        # draw footer background
        gint.dsubimage(self.left, self.bottom-5, res_button, resX, 27, 6, 8)
        xOffset = 5
        for x in range(self.left + xOffset, self.right-xOffset):
            gint.dsubimage(x,self.bottom-5, res_button, resX+7, 27, 1, 8)

        gint.dsubimage(self.right-xOffset, self.bottom-5, res_button, resX+6, 27, 6, 8)


        return super().Draw()

    def handleEvent(self, ev):
        if (self.flags & ButtonFlag.Enabled) and ( ev.type == gint.KEYEV_TOUCH_DOWN or ev.type == gint.KEYEV_TOUCH_UP):
            x,y = ev.x, ev.y
            if x >= self.left and x <= self.right and y >= self.top and y <= self.bottom:
                if ev.type == gint.KEYEV_TOUCH_DOWN:
                    self.pressed = True
                    self.Draw()
                    gint.dupdate()
                if ev.type == gint.KEYEV_TOUCH_UP:
                    return self.event_id
                
            elif ev.type == gint.KEYEV_TOUCH_DOWN: # Click outside
                    self.pressed = False
                    self.Draw()
                    gint.dupdate()
        return None
