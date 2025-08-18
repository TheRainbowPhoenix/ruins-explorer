# cpgame/game_plugins.py
# Contains custom functions callable by events via the PluginManager.

from cpgame.systems.jrpg import JRPG

def check_soil(event_id: int):
    """
    Plugin command to handle all interactions with a farm plot.
    Manages state transitions from untilled -> tilled -> planted -> harvest.
    """
    if JRPG.objects and JRPG.objects.map and JRPG.objects.growth_manager:
        map_id = JRPG.objects.map._map_id
        key_a = (map_id, event_id, 'A') # Tilled
        key_b = (map_id, event_id, 'B') # Planted
        key_d = (map_id, event_id, 'D') # Harvestable
        
        switches = JRPG.objects.self_switches
        
        if switches[key_d]: # Harvestable
            # Add item to party, reset plot
            # JRPG.objects.party.gain_item(5, 1)
            JRPG.objects.show_text(["You harvested a ripe potato!"])
            switches[key_a] = False
            switches[key_b] = False
            switches[key_d] = False
            JRPG.objects.growth_manager.harvest(map_id, event_id)

        elif switches[key_b]: # Planted
            status = JRPG.objects.growth_manager.get_status(map_id, event_id)
            JRPG.objects.show_text(["A small sprout is growing.", status])

        elif switches[key_a]: # Tilled
            # Placeholder for checking if player has seeds
            has_seeds = True # Assume true for now
            if has_seeds:
                JRPG.objects.show_text(["You planted a potato seed."])
                switches[key_b] = True
                # Grow for 20 seconds
                JRPG.objects.growth_manager.plant_seed(map_id, event_id, 20)
            else:
                JRPG.objects.show_text(["The soil is ready for seeds."])
                
        else: # Untilled
            JRPG.objects.show_text(["You tilled the soil."])
            switches[key_a] = True