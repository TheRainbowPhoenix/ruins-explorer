# cpgame/game_objects/party.py
# Manages the player's party of actors.

try:
    from typing import List
    from cpgame.game_objects.actor import GameActor
except:
    pass

class Game_Party:
    """
    Handles the player's party. Information such as the list of actors
    is included. An instance of this class will be held by the Game object.
    """
    def __init__(self):
        self._actors: List[int] = [] # Stores actor IDs

    def setup_starting_members(self, actor_ids: List[int]):
        """Initializes the party with the starting actors."""
        self._actors = []
        for actor_id in actor_ids:
            self.add_actor(actor_id)

    def members(self) -> List[int]:
        """Returns the list of actor IDs in the party."""
        return self._actors

    def add_actor(self, actor_id: int):
        """Adds an actor to the party by their ID if they are not already in it."""
        if actor_id not in self._actors:
            self._actors.append(actor_id)
            # In a full game, you might want to refresh the player's visuals here
            # e.g., $game_player.refresh()

    def remove_actor(self, actor_id: int):
        """Removes an actor from the party by their ID."""
        if actor_id in self._actors:
            self._actors.remove(actor_id)

    def size(self) -> int:
        """Returns the number of members in the party."""
        return len(self._actors)
