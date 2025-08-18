# cpgame/modules/game_objects.py
# This module manages all stateful game objects like actors, party, etc.

try:
    from typing import Dict, Any
    # Import the proxy class that this manager will use
except:
    pass

from cpgame.game_objects.map import GameMap
from cpgame.game_objects.party import GameParty
from cpgame.game_objects.character import GamePlayer
from cpgame.game_objects._actors import GameActors

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
        # self.switches = GameSwitches()
        # self.variables = GameVariables()

    def setup_new_game(self):
        """Sets up the initial state for a new game."""
        # In a real game, you would load starting actor IDs from system data
        # self.party.setup_starting_members(["ACTOR_1"])
        # You would also set initial player position, etc.
        pass

    def make_save_contents(self) -> Dict[str, Any]:
        """
        Creates a dictionary of all game state data to be saved.
        This method will be called when saving the game.
        """
        contents = {}
        # Each managed object is responsible for serializing its own state
        contents['actors'] = self.actors.to_dict()
        contents['party'] = self.party.to_dict()
        # contents['switches'] = self.switches.to_dict()
        # contents['variables'] = self.variables.to_dict()
        print("Saving game contents...")
        return contents

    def extract_save_contents(self, contents: Dict[str, Any]):
        """
        Loads game state from a save data dictionary.
        This method is called after loading a save file.
        """
        self.actors.from_dict(contents.get('actors', {}))
        self.party.from_dict(contents.get('party', {}))
        # self.switches.from_dict(contents.get('switches', {}))
        # self.variables.from_dict(contents.get('variables', {}))
        print("Extracted save contents.")