# cpgame/game_data/actors.py
# Contains data definitions for game actors.

# The HEADER is crucial for the DataManager to know what's available
# without loading the entire file.
HEADER = {
    'description': 'Contains all actor base data.',
    'exports': ['ACTOR_001', 'ACTOR_002'],
}

# Data for the first actor
ACTOR_001 = {
    "name": "Arion",
    "nickname": "The Valiant",
    "class_id": 1,
    "initial_level": 1,
    "character_name": "hero_sprite", # Assuming you have a sprite sheet named this
    "character_index": 0,
    "face_name": "hero_face",
    "face_index": 0,
    "equips": [1, 1, 2, 3, 0],
    "params": [100, 20, 12, 8, 5, 5, 10, 5], # MHP, MMP, ATK, DEF, MAT, MDF, AGI, LUK
    "description": [
        "A brave warrior from",
        "a small village.",
        "Destined for greatness."
    ]
}

# Data for a second actor
ACTOR_002 = {
    "name": "Lyra",
    "nickname": "The Sage",
    "class_id": 2,
    "initial_level": 1,
    "character_name": "mage_sprite",
    "character_index": 0,
    "face_name": "mage_face",
    "face_index": 0,
    "equips": [5, 0, 2, 4, 0],
    "params": [75, 50, 5, 6, 15, 12, 8, 7],
    "description": [
        "A wise mage with",
        "knowledge of ancient",
        "spells."
    ]
}