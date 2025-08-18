# cpgame/modules/game_objects.py
# This module manages all stateful game objects like actors, party, etc.

try:
    from typing import Dict, Any, List
    # Import the proxy class that this manager will use
except:
    pass

from cpgame.game_objects.map import GameMap
from cpgame.game_objects.party import GameParty
from cpgame.game_objects.character import GamePlayer
from cpgame.game_objects._actors import GameActors
from cpgame.game_objects.system import GameSystem
from cpgame.game_objects.variables import GameVariables
from cpgame.game_objects.switches import GameSwitches
from cpgame.game_objects.self_switches import GameSelfSwitches
from cpgame.game_objects.timer import GameTimer

# Plugins
from cpgame.modules.plugin_manager import PluginManager
from cpgame.modules.growth_manager import GrowthManager
from cpgame.game_plugins import check_soil

class GameObjects:
    """
    This class handles the creation and management of all runtime game objects
    that hold state, such as actors, the party, switches, and variables.
    It is the Python equivalent of the factory/manager part of DataManager
    that creates the $game_* objects.
    """
    def __init__(self):
        # The 'actors' property is a special proxy object that will lazy-load
        self.actors = GameActors()
        
        # Other game objects are instantiated directly but managed here.
        self.party = GameParty()
        self.player = GamePlayer()
        self.map = GameMap()
        self.system = GameSystem()
        self.switches = GameSwitches()
        self.self_switches = GameSelfSwitches()
        self.variables = GameVariables()
        self.timer = GameTimer()

        self.plugin_manager = PluginManager()
        self.growth_manager = GrowthManager()

        self.dialog_in_progress = False
        self.dialog_pages = []

    def setup_new_game(self):
        """Sets up the initial state for a new game."""
        from cpgame.systems.jrpg import JRPG

        self.plugin_manager.register("check_soil", check_soil)

        self.party.setup_starting_members()

        if JRPG.data and JRPG.data.system:
            self.map.setup(JRPG.data.system.get_or("start_map_id", 0))

            self.player.moveto(
                JRPG.data.system.get_or("start_x", 0),
                JRPG.data.system.get_or("start_y", 0)
            )
        

    def make_save_contents(self) -> Dict[str, Any]:
        """
        Creates a dictionary of all game state data to be saved.
        This method will be called when saving the game.
        """
        contents = {}
        # Each managed object is responsible for serializing its own state
        contents['actors'] = self.actors.to_dict()
        contents['party'] = self.party.to_dict()
        # contents['system'] = self.system.to_dict()
        contents['switches'] = self.switches.to_dict()
        contents['self_switches'] = self.self_switches.to_dict()
        contents['variables'] = self.variables.to_dict()
        # contents['timer'] = self.timer.to_dict() 
        print("Saving game contents...")
        return contents

    def extract_save_contents(self, contents: Dict[str, Any]):
        """
        Loads game state from a save data dictionary.
        This method is called after loading a save file.
        """
        self.actors.from_dict(contents.get('actors', {}))
        self.party.from_dict(contents.get('party', {}))
        # self.system.from_dict(contents.get('system', {}))
        self.switches.from_dict(contents.get('switches', {}))
        self.self_switches.from_dict(contents.get('self_switches', {}))
        self.variables.from_dict(contents.get('variables', {}))
        # self.timer.from_dict(contents.get('timer', {}))
        print("Extracted save contents.")

    # Debug stuff, should be later replaced by proper dialog system
    def show_text(self, pages: List[str]):
        """Flags that a dialog needs to be shown."""
        self.dialog_in_progress = True
        self.dialog_pages = pages

    def clear_dialog(self):
        """Clears the dialog state."""
        self.dialog_in_progress = False
        self.dialog_pages = []
