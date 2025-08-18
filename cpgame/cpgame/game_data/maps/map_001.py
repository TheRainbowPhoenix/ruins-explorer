HEADER = {
    'description': 'Village Map Data',
    'exports': ["displayName", "tilesetId", "width", "height", "scrollType", "specifyBattleback", "data", "events"],
}

displayName = "Quiet Village"
tilesetId = "jrpg" # Corresponds to the key in AssetManager
width = 13
height = 10
scrollType = 0
specifyBattleback = False
data = [
    1, 1, 1, 1, 5, 5, 5, 5, 5, 5, 1, 1, 1,
    1, 1, 1, 5, 5, 1, 1, 1, 5, 5, 1, 1, 1,
    1, 1, 5, 5, 1, 1, 1, 1, 1, 5, 5, 1, 1,
    1, 5, 5, 1, 1, 1, 1, 1, 1, 1, 5, 5, 1,
    5, 5, 1, 1, 1, 1, 1, 1, 1, 1, 1, 5, 5,
    5, 1, 1, 1, 1, 1, 1, 1, 5, 5, 5, 1, 5,
    5, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 5,
    5, 5, 1, 1, 1, 1, 1, 1, 1, 1, 1, 5, 5,
    1, 5, 5, 1, 1, 1, 1, 1, 1, 1, 5, 5, 1,
    1, 1, 5, 5, 5, 5, 5, 5, 5, 5, 5, 1, 1,
]
events = {
    # Event at (x=3, y=3)
    (3, 3): {
        "id": 1, "name": "ActorNPC",
        "pages": [{"graphic": {"tile_id": 56}, "payload": {"type": "actor", "id": 1}}]
    },
    # Event at (x=6, y=6)
    (6, 6): {
        "id": 2, "name": "Crystal",
        "pages": [{"graphic": {"tile_id": 52}, "payload": ["A strange crystal..."]}]
    },
    # Event at (x=10, y=2) - Teleport to Map 2
    (10, 2): {
        "id": 3, "name": "Portal",
        "pages": [{"graphic": {"tile_id": 60}, "payload": {"type": "transfer", "map_id": 2, "x": 5, "y": 5}}]
    }
}
