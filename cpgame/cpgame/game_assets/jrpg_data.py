# assets/jrpg_data.py
# Data for the JRPG scene, including a static map.

# Tile IDs that the player cannot walk on.
solid_tiles = {4} # The Sign ID

# A static map layout represented by tile IDs.
# 1=grass, 5=dirt_path
map_layout = [
    [1, 1, 1, 1, 5, 5, 5, 5, 5, 5, 1, 1, 1],
    [1, 1, 1, 5, 5, 1, 1, 1, 5, 5, 1, 1, 1],
    [1, 1, 5, 5, 1, 1, 1, 1, 1, 5, 5, 1, 1],
    [1, 5, 5, 1, 1, 1, 1, 1, 1, 1, 5, 5, 1],
    [5, 5, 1, 1, 1, 1, 1, 1, 1, 1, 1, 5, 5],
    [5, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 5],
    [5, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 5],
    [5, 5, 1, 1, 1, 1, 1, 1, 1, 1, 1, 5, 5],
    [1, 5, 5, 1, 1, 1, 1, 1, 1, 1, 5, 5, 1],
    [1, 1, 5, 5, 5, 5, 5, 5, 5, 5, 5, 1, 1],
]

# Data for interactive signs, mapping (y, x) coordinates to text.
map_signs = {
    (4, 6): ["A weathered sign...", "'Beware the Slimes'"]
}

# Data for interactive objects, mapping (y, x) to tile ID and text.
map_objects = {
    (6, 6): (52, ["You found a", "strange, glowing", "crystal."])
}