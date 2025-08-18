# cpgame/game_objects/self_switches.py
# Manages the state of event-local self switches.

try:
    from typing import Dict, Any, Tuple
except:
    pass

from cpgame.systems.jrpg import JRPG

class GameSelfSwitches:
    """This class handles self switches, using a composite key."""
    def __init__(self):
        self._data: Dict[Tuple[int, int, str], bool] = {}

    def __getitem__(self, key: Tuple[int, int, str]) -> bool:
        """Gets the value of a self switch, returning False if not set."""
        return self._data.get(key, False)
    
    def value(self, key: Tuple[int, int, str]) -> bool:
        """Gets the value of a self switch, returning False if not set."""
        return self._data.get(key, False)

    def __setitem__(self, key: Tuple[int, int, str], value: bool):
        """Sets the value of a self switch."""
        self._data[key] = value
        if JRPG.objects and JRPG.objects.map:
            JRPG.objects.map.need_refresh = True

    def set(self, key: Tuple[int, int, str], value: bool):
        """Sets the value of a self switch."""
        self._data[key] = value
        if JRPG.objects and JRPG.objects.map:
            JRPG.objects.map.need_refresh = True

    def to_dict(self) -> Dict[str, bool]:
        """Serializes the self switches for saving. Keys are converted to strings."""
        return {str(k): v for k, v in self._data.items()}

    def from_dict(self, data: Dict[str, bool]):
        """Loads self switch state from a dictionary."""
        self._data = {}
        if data:
            for k_str, v in data.items():
                # Convert string key back to tuple
                key_tuple = eval(k_str)
                self._data[key_tuple] = v