# scenes/jrpg_boot_scene.py
# Initializes the JRPG subsystem and transitions to the first JRPG scene.

from cpgame.engine.scene import Scene
from cpgame.game_scenes.jrpg_scene import JRPGScene

# Import the JRPG-specific systems we need to create
from cpgame.modules.datamanager import DataManager
from cpgame.game_objects.party import Game_Party

class JRPG_BootScene(Scene):
    """
    A special scene that sets up the JRPG 'session' objects
    (Party, DataManager, etc.) before the game starts.
    """
    def create(self):
        print("JRPG_BootScene: Initializing JRPG subsystem...")

        # Create instances of all JRPG-specific "global" objects
        data_manager = DataManager()
        party = Game_Party()

        # Initialize the starting party
        # In a real game, this might come from a system data file
        party.setup_starting_members(["ACTOR_001"]) # Start with Arion

        # Store these instances in the generic session container
        self.game.session_data['data'] = data_manager
        self.game.session_data['party'] = party
        
        # Immediately transition to the actual first scene of the JRPG
        self.game.change_scene(JRPGScene)

    def update(self, dt: float):
        # This scene does nothing in update, as it transitions instantly.
        pass

    def draw(self, frame_time_ms: int):
        # This scene does not need to draw anything.
        pass