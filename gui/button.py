from .base import GUIElement
import gint
from ._res import button as res_button

class ButtonFlag:
    Enabled = 1 << 15

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
