# cpgame/game_objects/variables.py
# Manages the state of in-game variables.

try:
    from typing import Dict, Any
except:
    pass

class Game_Variables:
    """
    This class handles game variables. It's a wrapper around a dictionary.
    An instance of this class is managed by Game_Objects.
    """
    def __init__(self):
        self._data: Dict[int, Any] = {}

    def __getitem__(self, variable_id: int) -> Any:
        """Gets the value of a variable, returning 0 if it's not set."""
        return self._data.get(variable_id, 0)

    def __setitem__(self, variable_id: int, value: Any):
        """Sets the value of a variable."""
        self._data[variable_id] = value

    def to_dict(self) -> Dict[int, Any]:
        """Serializes the variables for saving."""
        return self._data

    def from_dict(self, data: Dict[int, Any]):
        """Loads variable state from a dictionary."""
        self._data = data if data else {}
