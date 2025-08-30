# The HEADER is crucial for the DataManager to know what's available
# without loading the entire file.
HEADER = {
    'exports': [
        'ENEMY_1', 'ENEMY_2', 'ENEMY_3', 'ENEMY_4', 'ENEMY_5', 
        'ENEMY_6', 'ENEMY_7', 'ENEMY_8', 'ENEMY_9', 'ENEMY_10'
    ]
}

ENEMY_1 = {
    "id": 1,
    "name": "Slime",
    "params": [25, 10, 10, 5, 10, 5, 10, 10], # MHP, MMP, ATK, DEF, etc.
    "gold": 10,
    "exp": 5,
    # NEW: Battle-specific properties
    "attack_pattern": ["normal", "wait", "normal", "strong"],
    "minigame_difficulty": 1, # e.g., 1=slow, 5=fast
    "battler_name": None
}

ENEMY_2 = {
    "id": 2,
    "name": "Wild Wolf",
    "params": [40, 15, 15, 8, 12, 8, 15, 12],
    "gold": 15,
    "exp": 8,
    "attack_pattern": ["normal", "aggressive", "normal", "bite"],
    "minigame_difficulty": 2,
    "battler_name": None
}

ENEMY_3 = {
    "id": 3,
    "name": "Wild Boar",
    "params": [50, 10, 20, 12, 8, 10, 8, 8],
    "gold": 20,
    "exp": 12,
    "attack_pattern": ["charge", "normal", "charge", "tusk"],
    "minigame_difficulty": 3,
    "battler_name": None
}

ENEMY_4 = {
    "id": 4,
    "name": "Hungry Rabbit",
    "params": [30, 5, 8, 3, 5, 3, 20, 15],
    "gold": 8,
    "exp": 6,
    "attack_pattern": ["jump", "normal", "jump", "bite"],
    "minigame_difficulty": 2,
    "battler_name": "cabbit"
}

# Bosses 
ENEMY_5 = {
    "id": 5,
    "name": "Vorpal Rabbit",
    "params": [250, 30, 35, 25, 30, 20, 30, 25],
    "gold": 100,
    "exp": 50,
    "attack_pattern": ["slash", "teleport", "slash", "vorpal_strike"],
    "minigame_difficulty": 5,
    "battler_name": "vorpal"
}

ENEMY_6 = {
    "id": 6,
    "name": "Alien Cow",
    "params": [120, 40, 25, 20, 25, 15, 18, 12],
    "gold": 80,
    "exp": 40,
    "attack_pattern": ["moo", "beam", "moo", "alien_charge"],
    "minigame_difficulty": 4,
    "battler_name": None
}