# The HEADER is crucial for the DataManager to know what's available
# without loading the entire file.
HEADER = {
    'description': 'Contains all weapons.',
    'exports': ['WEAPON_1', 'WEAPON_2']
}

# In a farming game, "weapons" can be repurposed as "tools"
WEAPON_1 = {"id": 1, "name": "Hoe", "price": 150, "etype_id": 0, "params": [0,0,5,0,0,0,0,0], "description": "Used to till soil."}
WEAPON_2 = {"id": 2, "name": "Axe", "price": 200, "etype_id": 0, "params": [0,0,8,0,0,0,0,0], "description": "Used to chop wood."}

