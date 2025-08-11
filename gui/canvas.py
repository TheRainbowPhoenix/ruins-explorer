import gint

C_BLACK = gint.C_BLACK
C_WHITE = gint.C_WHITE
C_NONE = gint.C_NONE
DTEXT_LEFT = gint.DTEXT_LEFT

DTEXT_CENTER = gint.DTEXT_CENTER, 
DTEXT_RIGHT = gint.DTEXT_RIGHT,
    
DTEXT_TOP = gint.DTEXT_TOP, 
DTEXT_CENTER = gint.DTEXT_CENTER
DVCENTER = DTEXT_CENTER
DTEXT_BOTTOM = gint.DTEXT_BOTTOM

class GUIEvent:
    """
    Simple event object returned by get_event().
    type: "click", "key", or "user"
    pos: (x,y) for pointer events
    key: single-character string or special name ("ENTER", "BACKSPACE", etc.)
    event_id: for synthesized events (e.g. ENTER in a textbox)
    """
    def __init__(self, *, type, pos=None, key=None, event_id=None):
        self.type     = type
        self.pos      = pos
        self.key      = key
        self.event_id = event_id

class Canvas:
    # approximate cell size (pixels)
    char_width  = 8
    char_height = 16

    def clear(self, color: int = C_WHITE) -> None:
        """
        Fill the entire screen with `color`.
        """
        gint.dclear(color)

    def draw_rect(self, bounds: tuple[int,int,int,int]) -> None:
        """
        Draw a 1px‐bordered rectangle in C_BLACK, filled C_WHITE.
        """
        x1, y1, x2, y2 = bounds
        gint.drect_border(
            x1, y1, x2, y2,
            C_WHITE,
            1,
            C_BLACK
        )

    def draw_text(self,
                  text: str,
                  pos_or_bounds: tuple[int,int] | tuple[int,int,int,int],
                  fg: int = C_BLACK,
                  bg: int = C_NONE,
                  halign: int = DTEXT_LEFT,
                  valign: int = DTEXT_TOP,
                  wrap_width: int = -1
                  ) -> None:
        """
        Draw `text` at (x,y) or centered in a bounding box.
        - If pos_or_bounds is (x,y), text is drawn from that origin.
        - If pos_or_bounds is (x1,y1,x2,y2), text is centered in that rect.
        """
        if len(pos_or_bounds) == 2:
            x, y = pos_or_bounds
        else:
            x1, y1, x2, y2 = pos_or_bounds
            x = (x1 + x2) // 2
            y = (y1 + y2) // 2
            halign = DTEXT_CENTER
            valign = DVCENTER

        gint.dtext_opt(x, y, fg, bg, halign, valign, text, wrap_width)

    def draw_line(self,
                  start: tuple[int,int],
                  end:   tuple[int,int],
                  color: int = C_BLACK) -> None:
        """
        Draw a straight line from start to end.
        """
        x1, y1 = start
        x2, y2 = end
        gint.dline(x1, y1, x2, y2, color)

    def get_event(self) -> GUIEvent | None:
        """
        Poll for the next input event.
        Return a GUIEvent or None if no event pending.
        You'll need to wire this to your hardware event system.
        """
        ev = gint.pollevent()  # implement this in your gint binding
        if ev is None:
            return None

        return GUIEvent(
            type     = ev.type,         # e.g. "click" or "key"
            pos      = getattr(ev, "pos", None),
            key      = getattr(ev, "key", None),
            event_id = getattr(ev, "event_id", None)
        )

    def post_event(self, event_id: int) -> None:
        """
        Synthesize an event (e.g. ENTER from a textbox).
        """
        pass
        # gint.push_event({"type": "user", "event_id": event_id})

    def flush(self) -> None:
        """
        Commit all pending draw calls to the display.
        """
        gint.dupdate()