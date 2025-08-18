# cpgame/system/jrpg.py
# Acts as a Service Locator for all JRPG-specific "global" systems.


try:
    from typing import Optional, Union
    # Import types for clarity
    from cpgame.modules.datamanager import DataManager
    from cpgame.game_objects.party import GameParty
    from cpgame.modules.game_objects import GameObjects
except:
    pass

class JRPG:
    """
    A static class that holds references to all active JRPG subsystems.
    This provides a single, clean entry point for game objects to access
    systems like the party or data manager without using true globals.
    """
    # Class-level attributes to hold the system instances
    data: Optional['DataManager'] = None
    objects: Optional['GameObjects'] = None
    # Add other systems here as needed (e.g., system, timer)

    @classmethod
    def setup(cls, data_manager, game_objects):
        """Initializes the JRPG system with core objects."""
        # print("JRPG System: Setting up services.")
        cls.data = data_manager
        cls.objects = game_objects

    @classmethod
    def clear(cls):
        """Clears all references to allow for garbage collection."""
        # print("JRPG System: Clearing services.")
        cls.data = None
        cls.objects = None
    
    # Helpers
    @classmethod
    def is_data_state(cls, state_id: Union[int, str]) -> bool:
        if type(state_id) == int:
            name = "STATE_" + str(state_id) # TODO: name may change !! This is a workaround until i refactor data loader to return id linked to strings keys
        else:
            name = str(state_id)
        return cls.data is not None and cls.data.states.exists(name)
    
    @classmethod
    def get_actor(cls, actor_id):
        return cls.objects and cls.objects.actors and cls.objects.actors[actor_id] or None