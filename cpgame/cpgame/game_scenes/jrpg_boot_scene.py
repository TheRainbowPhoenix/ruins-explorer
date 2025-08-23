# scenes/jrpg_boot_scene.py
# Initializes the JRPG subsystem and transitions to the first JRPG scene.

from cpgame.engine.scene import Scene
from cpgame.game_scenes.jrpg_scene import JRPGScene
from cpgame.game_scenes.scene_map import SceneMap
from cpgame.modules.datamanager import DataManager
from cpgame.modules.game_objects import GameObjects
from cpgame.systems.jrpg import JRPG

class JRPG_BootScene(Scene):
    """
    A special scene that sets up the JRPG 'session' objects
    (Party, DataManager, etc.) before the game starts.
    """
    def create(self):
        # print("JRPG_BootScene: Initializing JRPG subsystem...")

        # Create instances of all JRPG-specific "global" objects
        data_manager = DataManager()
        # Temp fix to use DataManager in GameObjects
        JRPG.setup(data_manager=data_manager, game_objects=None, game=None)

        # party = GameParty()
        game_objects = GameObjects()
        # Store these instances in the generic session container
        # self.game.session_data['data'] = data_manager
        # self.game.session_data['objects'] = game_objects

        JRPG.setup(data_manager=data_manager, game_objects=game_objects, game=self.game)

        # Set up a new game state within the game objects manager
        game_objects.setup_new_game()
        data_manager.init()
        
        
        # Immediately transition to the actual first scene of the JRPG
        self.game.change_scene(SceneMap) # JRPGScene

    def update(self, dt: float):
        # This scene does nothing in update, as it transitions instantly.
        pass

    def draw(self, frame_time_ms: int):
        # This scene does not need to draw anything.
        pass