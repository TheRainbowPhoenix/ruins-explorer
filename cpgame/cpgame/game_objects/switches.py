# cpgame/game_objects/switches.py
# Manages the state of in-game switches.

try:
    from typing import Dict, Any
except:
    pass

class GameSwitches:
    """
    This class handles game switches. It's a wrapper around a dictionary.
    """
    def __init__(self):
        self._data: Dict[int, bool] = {}

    def __getitem__(self, switch_id: int) -> bool:
        """Gets the value of a switch, returning False if not set."""
        return self._data.get(switch_id, False)

    def __setitem__(self, switch_id: int, value: bool):
        """Sets the value of a switch."""
        self._data[switch_id] = value

    def value(self, switch_id: int) -> bool:
        """Gets the value of a switch, returning False if not set."""
        return self._data.get(switch_id, False)

    def to_dict(self) -> Dict[int, bool]:
        return self._data

    def from_dict(self, data: Dict[int, bool]):
        self._data = data if data else {}