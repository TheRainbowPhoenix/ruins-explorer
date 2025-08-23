# cpgame/game_windows/window_hud.py
# The Heads-Up Display for the map screen.

from gint import *
from cpgame.game_windows.window_base import WindowBase
from cpgame.systems.jrpg import JRPG

class WindowHUD(WindowBase):
    def __init__(self):
        super().__init__(0, 0, DWIDTH, 28)

    def draw(self):
        if not self.visible: return
        self._draw_skin()
        
        if not JRPG.objects: return

        # Draw Score (Variable 1)
        score = JRPG.objects.variables[1]
        dtext(self.x + self.padding, self.y + 4, C_BLACK, "Score: " + str(score))

        # Draw Gold
        gold = str(JRPG.objects.party.gold) + " G"
        w, _ = dsize(gold, None) if 'dsize' in globals() else (len(gold) * 8, 16)
        dtext(self.x + self.width - self.padding - w, self.y + 4, C_BLACK, gold)

        # Draw Day
        day = int(JRPG.objects.timer.total_play_time // 120) + 1 # 1 day = 2 minutes
        day_text = "Day " + str(day)
        w, _ = dsize(day_text, None) if 'dsize' in globals() else (len(day_text) * 8, 16)
        dtext(self.x + (self.width - w) // 2, self.y + 4, C_BLACK, day_text)