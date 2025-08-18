# cpgame/game_plugins.py
# Contains custom functions callable by events via the PluginManager.

from cpgame.systems.jrpg import JRPG

def check_soil(event_id: int):
    """
    Plugin command to handle all interactions with a farm plot.
    Manages state transitions from untilled -> tilled -> planted -> harvest.
    """
    if not JRPG.objects or not JRPG.objects.map or not JRPG.objects.growth_manager:
        return

    map_id = JRPG.objects.map._map_id
    key_a = (map_id, event_id, 'A') # Tilled
    key_b = (map_id, event_id, 'B') # Planted
    key_d = (map_id, event_id, 'D') # Harvestable
    
    switches = JRPG.objects.self_switches
    message = JRPG.objects.message
    message.clear() # Always start with a fresh message

    if switches[key_d]: # Harvestable
        # Add item to party, reset plot
        # TODO: JRPG.objects.party.gain_item(5, 1)
        message.add("You harvested a ripe potato!")
        JRPG.objects.self_switches.set(key_a, False)
        JRPG.objects.self_switches.set(key_b, False)
        JRPG.objects.self_switches.set(key_d, False)
        JRPG.objects.growth_manager.harvest(map_id, event_id)

    elif switches[key_b]: # Planted
        status = JRPG.objects.growth_manager.get_status(map_id, event_id)
        message.add("A small sprout is growing.")
        message.add(status)

    elif switches[key_a]: # Tilled
        # Placeholder for checking if player has seeds
        has_seeds = True # Assume true for now
        if has_seeds:
            message.add("You planted a potato seed.")
            JRPG.objects.self_switches.set(key_b, True)
            # Grow for 20 seconds
            JRPG.objects.growth_manager.plant_seed(map_id, event_id, 20)
        else:
            message.add("The soil is ready for seeds.")
            
    else: # Untilled
        message.add("You tilled the soil.")
        JRPG.objects.self_switches.set(key_a, True)

    for ev in JRPG.objects.map.events.values():
        if ev.id == event_id:
            ev.refresh()
            break