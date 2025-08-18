# cpgame/modules/growth_manager.py
# Manages the growth cycles of plants and other timed map objects.

try:
    from typing import Dict, Any, Tuple
except:
    pass

from cpgame.systems.jrpg import JRPG
from cpgame.engine.logger import log

class GrowthManager:
    def __init__(self):
        # Key: (map_id, event_id), Value: {"state": str, "ends_at": float}
        self._growing_objects: Dict[Tuple[int, int], Dict] = {}

    def plant_seed(self, map_id: int, event_id: int, duration: int):
        """Registers a new plant to start its growth cycle."""
        key = (map_id, event_id)
        if key in self._growing_objects:
            return # Already growing
        
        if JRPG.objects and JRPG.objects.timer:
            current_time = JRPG.objects.timer.total_play_time
            self._growing_objects[key] = {
                "state": "growing",
                "ends_at": current_time + duration
            }
            log("GrowthManager: Plant registered at ({}, {}). Finishes in {}s.".format(map_id, event_id, duration))

    def get_status(self, map_id: int, event_id: int) -> str:
        """Gets the current growth status of an object."""
        obj = self._growing_objects.get((map_id, event_id))
        if not obj:
            return "none"
        if obj["state"] == "harvestable":
            return "harvestable"
        
        if JRPG.objects and JRPG.objects.timer:
            remaining = obj["ends_at"] - JRPG.objects.timer.total_play_time
            return "Growing ({}s left)".format(int(remaining))
        return "none"

    def harvest(self, map_id: int, event_id: int):
        """Removes an object from the manager after harvesting."""
        key = (map_id, event_id)
        if key in self._growing_objects:
            del self._growing_objects[key]
            log("GrowthManager: Harvested object at ({}, {}).".format(map_id, event_id))

    def update(self, dt: float):
        """Checks all growing objects to see if they are ready."""
        if JRPG.objects and JRPG.objects.timer and JRPG.objects.self_switches:
            current_time = JRPG.objects.timer.total_play_time
            # Iterate over a copy of keys since we may modify the dictionary
            for key in list(self._growing_objects.keys()):
                obj = self._growing_objects[key]
                if obj["state"] == "growing" and current_time >= obj["ends_at"]:
                    obj["state"] = "harvestable"
                    # Set the event's 'D' switch to ON to change its page to harvestable
                    JRPG.objects.self_switches[(key[0], key[1], 'D')] = True
                    log("GrowthManager: Object at {} is now harvestable!".format(key))
    