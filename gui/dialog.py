import gint
from .base import GUIElement, Wrapped, hex_to_rgb
from ._res import dialog as res_dialog

class GUIDialogHeight:
    Height25 = 0
    Height55 = 1
    Height75 = 2
    Height95 = 3
    Height35 = 4
    Height60 = 5

class GUIDialogAlignment:
    AlignTop = 0
    AlignCenter = 1
    AlignBottom = 2

class GUIDialogKeyboardState:
    KeyboardStateNone = 0
    KeyboardStateMath1 = 1
    KeyboardStateMath2 = 4
    KeyboardStateMath3 = 5
    KeyboardStateTrig = 6
    KeyboardStateVar = 7
    KeyboardStateABC = 8
    KeyboardStateCatalog = 9
    KeyboardStateAdvance = 10
    KeyboardStateNumber = 11

class DialogResult:
    OK = 0x3EA
    Cancel = 0x3EB

class GUIDialog(Wrapped):
    HEADER_SIZE = 31
    
    def __init__(self,
                 height: int,
                 alignment: int,
                 title: str,
                 keyboard: int):
        super().__init__()
        self.title = title
        # compute geometry
        DW = gint.DWIDTH
        DH = gint.DHEIGHT
        self.elements: list[Wrapped] = []

        # determine dialog height in px
        if height == GUIDialogHeight.Height25:
            dlg_h = round(DH * 0.25 - 6)
        elif height == GUIDialogHeight.Height35:
            dlg_h = round(DH * 0.35 - 6)
        elif height == GUIDialogHeight.Height55:
            dlg_h = round(DH * 0.55 - 6)
        elif height == GUIDialogHeight.Height60:
            dlg_h = round(DH * 0.60 - 6)
        elif height == GUIDialogHeight.Height75:
            dlg_h = round(DH * 0.75 - 6)
        elif height == GUIDialogHeight.Height95:
            dlg_h = round(DH * 0.95 - 6)
        else:
            dlg_h = round(DH * 0.5 - 6)
        # vertical position
        if alignment == GUIDialogAlignment.AlignTop:
            top = 0
        elif alignment == GUIDialogAlignment.AlignCenter:
            top = (DH - dlg_h) // 2
        else:
            top = DH - dlg_h
        
        bottom = top + dlg_h
        # horizontal
        left = 3
        right = DW - left
        self.leftX, self.topY = left, top
        self.rightX, self.bottomY = right, bottom

    def Draw(self):

        # draw header background
        xOffset = 5
        yOffset = 11

        gint.drect(
            self.leftX+xOffset, self.topY+yOffset,
            self.rightX-xOffset, self.topY +yOffset+ 16,
            gint.C_RGB(13,13,13)
        )

        gint.dsubimage(self.leftX, self.topY, res_dialog, 0, 0, 5, 38)
        
        for x in range(self.leftX + xOffset, self.rightX-xOffset):
            gint.dsubimage(x, self.topY, res_dialog, 5, 0, 1, 38)

        gint.dsubimage(self.rightX-xOffset, self.topY, res_dialog, 6, 0, 5, 38)
        

        gint.dtext_opt(
            self.leftX + 12, self.topY + 8,
            gint.C_WHITE,
            gint.C_NONE,
            gint.DTEXT_LEFT, gint.DTEXT_TOP,
            self.title,
            -1
        )
        # fill body background
        gint.drect(
            self.leftX + 5,
            self.topY + 36,
            self.rightX - 5,
            self.bottomY - 5 - 7,
            gint.C_WHITE
        )

        yOffset = 36
        for y in range(self.topY + yOffset, self.bottomY-5-7):
            gint.dsubimage(self.leftX, y, res_dialog, 0, 37, 6, 1)
            gint.dsubimage(self.rightX - 5, y, res_dialog, 6, 37, 5, 1)

        # draw footer background
        gint.dsubimage(self.leftX, self.bottomY-5-7, res_dialog, 0, 38, 6, 7)
        xOffset = 5
        for x in range(self.leftX + xOffset, self.rightX-xOffset):
            gint.dsubimage(x,self.bottomY-5-7, res_dialog, 5, 38, 1, 7)

        gint.dsubimage(self.rightX-xOffset, self.bottomY-5-7, res_dialog, 6, 38, 5, 7)

    def EndDraw(self):
        # could draw shadows or cleanup
        pass

    def AddElement(self, elem: Wrapped):
        self.Add(elem)

    def ShowDialog(self):
        # initial draw
        self.do_draw()
        # wait for close event loop
        while True:
            ev = gint.pollevent()
            if ev and ( ev.type == gint.KEYEV_TOUCH_DOWN or ev.type == gint.KEYEV_TOUCH_UP):
                x,y = ev.x, ev.y
                # close button assumed bound to DialogResultCancel event
                if x >= self.leftX and x <= self.rightX and y >= self.topY and y <= self.bottomY:
                    # dispatch to elements
                    for el in self.children:
                        event_id = el.handleEvent(ev) # TODO: should be data struct
                        if event_id:
                            r = self.OnEvent(event_id)
                            if r:
                                return r
                            
        return DialogResult.Cancel
    
    

    def GetLeftX(self):   return self.leftX + 6
    def GetTopY(self):    return self.topY + 37
    def GetRightX(self):  return self.rightX - 6
    def GetBottomY(self): return self.bottomY - 7 - 5


    # def Refresh(self):
    #     self._canvas.clear()
    #     for el in self.elements:
    #         el.render(self._canvas)
    #     self._canvas.flush()

    # def ShowDialog(self, canvas):
    #     self._canvas = canvas
    #     self.Refresh()
    #     while True:
    #         ev = canvas.get_event()
    #         # dispatch to elements
    #         for el in self.elements:
    #             if el.handleEvent(ev):
    #                 if ev.event_id == DialogResult.OK:
    #                     return DialogResult.OK
    #                 if ev.event_id == DialogResult.Cancel:
    #                     return DialogResult.Cancel
            # optional: allow subclass OnEvent to handle
