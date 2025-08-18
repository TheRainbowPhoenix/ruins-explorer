# This would manage all growing things on the current map.
# It would be updated once per frame in the JRPGScene.


from cpgame.systems.jrpg import JRPG

class GrowthManager:
    def __init__(self):
        # (map_id, event_id) -> growth_end_time
        self._growing_plants = {}

    def register_plant(self, map_id, event_id, growth_duration_seconds):
        if JRPG.objects and JRPG.objects.timer:
            current_time = JRPG.objects.timer.get_total_play_time() # Needs a new timer feature
        
            self._growing_plants[(map_id, event_id)] = current_time + growth_duration_seconds

    def update(self):
        if JRPG.objects and JRPG.objects.timer:
            current_time = JRPG.objects.timer.get_total_play_time()
            for key, end_time in self._growing_plants.items():
                if current_time >= end_time:
                    # The plant is grown! Set its event's Self Switch.
                    map_id, event_id = key
                    JRPG.objects.self_switches[(map_id, event_id, 'D')] = True
                    # Remove from this manager
                    del self._growing_plants[key]