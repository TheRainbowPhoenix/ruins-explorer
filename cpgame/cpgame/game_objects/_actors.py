# cpgame/game_objects/actors.py
# The proxy class for managing all Game_Actor instances.

try:
    from typing import Dict, Optional
    # service locator to get the data manager
except:
    pass

from cpgame.engine.logger import log
from cpgame.systems.jrpg import JRPG
from cpgame.game_objects.actor import GameActor

class GameActors:
    """
    A proxy class that manages all Game_Actor instances.
    It creates actors on-demand (lazy instantiation) and holds them
    in a cache for the duration of the session.
    """
    def __init__(self):
        self._instances: Dict[str, 'GameActor'] = {}
        self._saved_states: Dict[str, Dict] = {}

    def __getitem__(self, actor_id: int) -> Optional['GameActor']:
        """
        Provides access to an actor instance, creating it if it doesn't exist.
        This is the core of the lazy-loading mechanism.
        """
        actor_name_id = "ACTOR_" + str(actor_id)
        if actor_name_id in self._instances:
            return self._instances[actor_name_id]

        # Ensure the actor ID exists in the database before trying to load
        if not JRPG.data or not JRPG.data.actors.exists(actor_name_id):
            print("Warning: Attempted to access non-existent actor:", actor_name_id)
            return None

        # print("Instantiating actor for the first time:", actor_id)
        # Load the base data using the DataManager's context manager
        with JRPG.data.actors.load(actor_name_id) as actor_data:
            if actor_data:
                # Create the new instance
                actor = GameActor(actor_id, actor_data)
                
                # If there's saved state for this actor, apply it
                if actor_id in self._saved_states:
                    log("Applying saved state to", actor_id)
                    actor.from_dict(self._saved_states[actor_id])

                # Cache the new instance and return it
                self._instances[actor_name_id] = actor
                return actor
        return None

    def to_dict(self) -> Dict[str, Dict]:
        """Serializes the state of all currently instantiated actors."""
        serialized_actors = {}
        for actor_id, instance in self._instances.items():
            serialized_actors[actor_id] = instance.to_dict()
        return serialized_actors

    def from_dict(self, data: Dict[str, Dict]):
        """
        Stores saved state data. This does not create instances yet;
        it prepares the proxy for lazy-loading actors with saved data.
        """
        self._instances = {}  # Clear any existing instances
        self._saved_states = data