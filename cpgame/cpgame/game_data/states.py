# Contains data definitions for status effects (states).

HEADER = {
    'description': 'Contains all state data.',
    'exports': ['STATE_1', 'STATE_4'], # Exporting Death and Poison
}

# State ID 1: Death (Knockout)
STATE_1 = {
    "id": 1,
    "name": "Knockout",
    "priority": 100,
    "restriction": 4, # Cannot act
    "message1": "falls!",
    "message2": "falls!",
    "message4": "is revived!",
}

# State ID 4: Poison (full verbose)
STATE_4 = {
    "id": 4,
    "name": "Poison",
    "icon_index": 18,
    "priority": 65,
    "restriction": 0,
    "auto_removal_timing": 2,
    "min_turns": 3,
    "max_turns": 3,
    "remove_by_damage": False,
    "remove_by_walking": False,
    "remove_by_restriction": False,
    "remove_at_battle_end": True,
    "chance_by_damage": 100,
    "steps_to_remove": 100,
    "message1": "is poisoned!",
    "message2": "is poisoned!",
    "message3": "",
    "message4": " is freed of poison!",
    "motion": 0,
    "overlay": 0,
    "note": "pop add[Poisoned]\r\npop remove[]",
    "traits": [
      {
        "code": 22,
        "dataId": 7,
        "value": -0.1
      }
    ]
}