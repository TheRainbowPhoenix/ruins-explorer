# cpgame/game_objects/actor.py
# Represents an Actor (character) in the game, adapted from Game_Actor.

try:
    from typing import Dict, Any, List
except:
    pass

class GameActor:
    """
    Handles actor data. It is used within Game_Actors and Game_Party.
    This class is data-driven, initialized from a dictionary.
    """
    def __init__(self, actor_id: int, actor_data: Dict[str, Any]):
        self.id = actor_id
        self.name: str = actor_data.get("name", "Actor")
        self.nickname: str = actor_data.get("nickname", "")
        self.class_id: int = actor_data.get("class_id", 1)
        self.level: int = actor_data.get("initial_level", 1)
        
        # Graphics
        self.character_name: str = actor_data.get("character_name", "")
        self.character_index: int = actor_data.get("character_index", 0)
        self.face_name: str = actor_data.get("face_name", "")
        self.face_index: int = actor_data.get("face_index", 0)

        # Base Parameters
        # In a full implementation, these would come from a class_data module
        self.mhp: int = actor_data.get("params", [50, 0, 0, 0, 0, 0, 0, 0])[0]
        self.mmp: int = actor_data.get("params", [0, 50, 0, 0, 0, 0, 0, 0])[1]
        self.atk: int = actor_data.get("params", [0, 0, 10, 0, 0, 0, 0, 0])[2]
        self.defe: int = actor_data.get("params", [0, 0, 0, 10, 0, 0, 0, 0])[3]
        
        # Current stats
        self.hp: int = self.mhp
        self.mp: int = self.mmp
        
        self.description: List[str] = actor_data.get("description", ["A mysterious hero."])

    def get_info_text(self) -> List[str]:
        """Returns a formatted list of strings with the actor's info."""
        info = [self.name + ", Lvl " + str(self.level)]
        info.extend(self.description)
        return info