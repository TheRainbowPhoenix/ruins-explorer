# scenes/menu_scene.py
# The initial scene that lets the player choose a game.
import gint
from cpgame.engine.scene import Scene
from cpgame.modules.datamanager import ClassProxy
# from cpgame.game_scenes.templar_scene import TemplarScene
# MODIFIED: Import the boot scene instead of the main JRPG scene
from cpgame.game_scenes.jrpg_boot_scene import JRPG_BootScene
from cpgame.modules.pakloader import PakProxy

C_YELLOW = 0b00000_111111_11111
BG_COLOR = gint.C_RGB(2, 7, 4)

class MenuScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.options = ["Play Game", "Exit"]
        self.selected_index = 0
        self.redraw_needed = True
        self._full_redraw = True

    def update(self, dt: float) -> None:
        """Update is called once per logic frame."""
        # Get a snapshot of the input for this frame.
        # self.input.update()

        # Use the new one-shot `up` and `down` properties for snappy menu navigation.
        if self.input.up:
            self.selected_index = (self.selected_index - 1 + len(self.options)) % len(self.options)
            self.redraw_needed = True
        
        if self.input.down:
            self.selected_index = (self.selected_index + 1) % len(self.options)
            self.redraw_needed = True
        
        # Check for the interact button press to make a selection.
        if self.input.interact:
            if self.selected_index == 0:
            #     self.game.change_scene(TemplarScene)
            # elif self.selected_index == 1:
                self.game.change_scene(JRPG_BootScene)
            elif self.selected_index == 1:
                self.game.running = False # Signal the game to exit
        
        # Also allow exiting with the EXIT key.
        if self.input.exit:
            self.game.running = False

    def create(self):
        # return super().create()
        self._pak = PakProxy()


    def draw(self, frame_time_ms: int):
        """Draw is called once per render frame."""
        # Only redraw the screen if something has changed.
        
        if self._full_redraw:
            
            gint.dupdate()
            gint.dclear(BG_COLOR)
            gint.drect(0,0,gint.DWIDTH, gint.DHEIGHT, BG_COLOR)

            logo_x = (gint.DWIDTH-192)//2
            # gint.dwindow_set(logo_x, 0, logo_x+192, 158)
            # gint.drect(logo_x, 0, logo_x+192, 158, BG_COLOR)
            # gint.dupdate()
            # drect(logo_x+1, 1, logo_x+190, 158, C_RGB(29, 31, 13))
            # with ClassProxy('cpgame.modules.pakloader', 'PakProxy') as pak_proxy:
            
            # gint.dupdate()
            # gint.dclear(BG_COLOR)
            # gint.drect(0,0,gint.DWIDTH, gint.DHEIGHT, BG_COLOR)
        
            

            self._pak.draw_from(logo_x, 0, 'faces.pak', 'logo', 192+logo_x)
            self._pak.clear_cache()
            # gint.dupdate()
            # gint.dwindow_set(0, 0, gint.DWIDTH, gint.DHEIGHT)
        
            self._full_redraw = False
        
        if not self.redraw_needed:
            return

        # x = 96
        # w = 128
        gint.drect(96, 160, 96+128, 224, gint.C_RGB(2, 7, 4))
        
        # dtext_opt(DWIDTH//2, 50, C_WHITE, C_NONE, DTEXT_CENTER, DTEXT_TOP, ">Touch Grass", -1)
        
        for i, option in enumerate(self.options):
            color = C_YELLOW if i == self.selected_index else gint.C_WHITE
            gint.dtext_opt(gint.DWIDTH//2, 150 + i * 25, color, gint.C_NONE, gint.DTEXT_CENTER, gint.DTEXT_TOP, option, -1)
            
        self.redraw_needed = False
    
    def destroy(self):
        del self._pak
        return super().destroy()