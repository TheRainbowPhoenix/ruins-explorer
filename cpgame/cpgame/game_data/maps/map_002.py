HEADER = {
    'description': 'Cave Map Data',
    'exports': ["displayName", "tilesetId", "width", "height", "scrollType", "specifyBattleback", "data", "events"],
}

displayName = "Mysterious Cave"
tilesetId = "jrpg" # Corresponds to the key in AssetManager
width = 10
height = 10
scrollType = 0
specifyBattleback = False
data = [
    4, 4, 4, 4, 4, 4, 4, 4, 4, 4,
    4, 5, 5, 5, 1, 1, 5, 5, 5, 4,
    4, 5, 1, 1, 1, 1, 1, 1, 5, 4,
    4, 5, 1, 1, 1, 1, 1, 1, 5, 4,
    4, 1, 1, 1, 1, 1, 1, 1, 1, 4,
    4, 1, 1, 1, 1, 1, 1, 1, 1, 4,
    4, 5, 1, 1, 1, 1, 1, 1, 5, 4,
    4, 5, 5, 5, 1, 1, 5, 5, 5, 4,
    4, 4, 4, 4, 4, 4, 4, 4, 4, 4,
    4, 4, 4, 4, 4, 4, 4, 4, 4, 4,
]
events = {
    (5, 5): {
        "id": 1, "name": "ReturnPortal",
        "pages": [{"graphic": {"tile_id": 60}, "payload": {"type": "transfer", "map_id": 1, "x": 10, "y": 3}}]
    }
}
