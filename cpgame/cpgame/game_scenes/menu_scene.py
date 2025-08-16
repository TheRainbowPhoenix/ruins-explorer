# scenes/menu_scene.py
# The initial scene that lets the player choose a game.
from gint import *
from cpgame.engine.scene import Scene
from cpgame.game_scenes.templar_scene import TemplarScene
from cpgame.game_scenes.jrpg_scene import JRPGScene

C_YELLOW = 0b00000_111111_11111

class MenuScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.options = ["Play Platformer (Templar)", "Play Top-Down (JRPG)", "Exit"]
        self.selected_index = 0
        self.redraw_needed = True

    def update(self, dt: float) -> None:
        """Update is called once per logic frame."""
        # Get a snapshot of the input for this frame.
        self.input.update()

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
                self.game.change_scene(TemplarScene)
            elif self.selected_index == 1:
                self.game.change_scene(JRPGScene)
            elif self.selected_index == 2:
                self.game.running = False # Signal the game to exit
        
        # Also allow exiting with the EXIT key.
        if self.input.exit:
            self.game.running = False

    def draw(self, frame_time_ms: int):
        """Draw is called once per render frame."""
        # Only redraw the screen if something has changed.
        if not self.redraw_needed:
            return
            
        dclear(C_RGB(2, 5, 10))
        dtext_opt(DWIDTH//2, 50, C_WHITE, C_NONE, DTEXT_CENTER, DTEXT_TOP, "CPGAME ENGINE DEMO", -1)
        
        for i, option in enumerate(self.options):
            color = C_YELLOW if i == self.selected_index else C_WHITE
            dtext_opt(DWIDTH//2, 150 + i * 25, color, C_NONE, DTEXT_CENTER, DTEXT_TOP, option, -1)
            
        self.redraw_needed = False