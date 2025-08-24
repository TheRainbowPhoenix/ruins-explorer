# cpgame/game_windows/window_message.py
# The window that displays the content of GameMessage.
import gint
# from cpgame.game_windows.window_base import WindowBase
from cpgame.systems.jrpg import JRPG
from cpgame.engine.text_parser import parse_text_codes
from cpgame.modules.datamanager import ClassProxy
from cpgame.engine.logger import log
from cpgame.modules.pakloader import PakProxy

# Use const for optimized, unchanging values
from micropython import const
_TEXT_BOX_WIDTH = gint.DWIDTH
_TEXT_BOX_HEIGHT = const(100)
_PADDING = const(10)
_LINE_HEIGHT = const(16)

_FACE_BOX_SIZE = const(96)
_FACE_BOX_PADDING = const(4)

# Custom window colors
_BG_COLOR = gint.C_RGB(30, 26, 13)
_BORDER_OUTER_COLOR = gint.C_RGB(18, 10, 2)
_BORDER_INNER_COLOR = gint.C_RGB(29, 22, 8)
_TEXT_COLOR = gint.C_RGB(5, 2, 0)

class WindowMessage:
    """A lightweight, standalone window for displaying dialogue and portraits."""
    def __init__(self):
        # State
        self.visible = False
        self.openness = 0  # Used for fade-in/out animation
        self._wait_for_input = False
        
        # --- Caching ---
        # Cache face details to prevent redrawing the (slow) portrait every frame
        self._cached_face_name = None
        self._needs_redraw = True

    def destroy(self):
        self.visible = False
        # Clear caches to release references
        self._cached_face_name = None

    def update(self):
        """Updates the window's visibility and open/close animation."""
        if JRPG.objects and JRPG.objects.message.is_text():
            if not self.visible:
                # This is the first frame the message is active, trigger full redraw
                self._needs_redraw = True
                self.visible = True
                
            if self.openness < 255:
                self.openness = min(255, self.openness + 48)
            
            # Check for input to close the message
            # if self._wait_for_input and JRPG.input.interact:
            #     self.terminate_message()

        else:
            if self.openness > 0:
                self.openness = max(0, self.openness - 48)
            else:
                self.visible = False


    def on_confirm(self, input=None):
        """
        Called by the scene when the player presses the interact button.
        This is the correct way to handle input, decoupling the window from the input system.
        """
        if self.is_ready_for_input():
            self.terminate_message()
            # if JRPG.objects: JRPG.objects.message.clear()

    def is_ready_for_input(self) -> bool:
        """Checks if the message is fully open and waiting for input."""
        return self.visible and self.openness >= 255 and self._wait_for_input

    def terminate_message(self):
        """Closes the window and clears the central message data."""
        self.openness = 0
        self.visible = False
        self._wait_for_input = False
        self._cached_face_name = None
        if JRPG.objects: JRPG.objects.message.clear()

    @property
    def y(self):
        return gint.DHEIGHT - _TEXT_BOX_HEIGHT

    def draw(self):
        if not self.visible or self.openness < 255:
            return
        # TODO: openness effect ?
        
        if not JRPG.objects: return
        message = JRPG.objects.message
        
        # --- Layout Calculations ---
        # Text box is always at the bottom
        text_box_y = gint.DHEIGHT - _TEXT_BOX_HEIGHT
        
        # Face box is positioned above and to the left of the text box
        face_box_x = _PADDING
        face_box_y = text_box_y - _FACE_BOX_SIZE - _PADDING

        # Draw the main text box
        gint.drect(0, text_box_y, _TEXT_BOX_WIDTH - 1, gint.DHEIGHT - 1, _BG_COLOR)
        gint.drect_border(0, text_box_y, _TEXT_BOX_WIDTH, gint.DHEIGHT, gint.C_NONE, 1, _BORDER_OUTER_COLOR)
        gint.drect_border(1, text_box_y + 1, _TEXT_BOX_WIDTH - 1, gint.DHEIGHT - 1, gint.C_NONE, 1, _BORDER_INNER_COLOR)
        
        # Draw the face and its box, if one is specified
        if message.face_name:
            # Only redraw the slow face asset if the face has changed
            if self._cached_face_name != message.face_name:
                # Draw the face box skin
                gint.drect(face_box_x, face_box_y, face_box_x + _FACE_BOX_SIZE - 1, face_box_y + _FACE_BOX_SIZE - 1, _BG_COLOR)
                gint.drect_border(face_box_x, face_box_y, face_box_x + _FACE_BOX_SIZE, face_box_y + _FACE_BOX_SIZE, gint.C_NONE, 1, _BORDER_OUTER_COLOR)
                gint.drect_border(face_box_x + 1, face_box_y + 1, face_box_x + _FACE_BOX_SIZE - 1, face_box_y + _FACE_BOX_SIZE - 1, gint.C_NONE, 1, _BORDER_INNER_COLOR)

                self._cached_face_name = message.face_name
                log("Drawing new face:", message.face_name)

                pak_proxy = PakProxy()
                # Use a ClassProxy to load and draw the face from the PAK file
                # with ClassProxy('cpgame.modules.pakloader', '') as pak_proxy:
                # Correctly calculate the drawing coordinates and clipping area
                draw_x = face_box_x # + _FACE_BOX_PADDING
                draw_y = face_box_y # + _FACE_BOX_PADDING
                clip_x_end = draw_x + _FACE_BOX_SIZE # - (_FACE_BOX_PADDING * 2)
                
                # The last argument tells the proxy the max x-coordinate to draw to
                pak_proxy.draw_from(draw_x, draw_y, 'faces.pak', message.face_name, clip_x_end)
                del pak_proxy

        # Draw Text and Continue Indicator (only when fully open)
        if self.openness >= 255:
            for i, line in enumerate(message.texts):
                final_text = parse_text_codes(line)
                gint.dtext(_PADDING, text_box_y + _PADDING + i * _LINE_HEIGHT, _TEXT_COLOR, final_text)
                # gint.dupdate() # slow but make a "test appear" effect

            self._wait_for_input = True
            # Draw the continue indicator triangle
            tri_x = _TEXT_BOX_WIDTH - _PADDING - 12
            tri_y = gint.DHEIGHT - _PADDING - 6
            gint.dline(tri_x, tri_y, tri_x + 6, tri_y - 6, _BORDER_OUTER_COLOR)
            gint.dline(tri_x + 6, tri_y - 6, tri_x + 12, tri_y, _BORDER_OUTER_COLOR)
            gint.dline(tri_x + 12, tri_y, tri_x, tri_y, _BORDER_OUTER_COLOR)