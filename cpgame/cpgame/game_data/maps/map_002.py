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
    (5, 6): {
        "id": 3, "name": "ReturnPortal", "x": 5, "y": 6,
        "pages": [{
            "graphic": {"tileId": 60},
            "list": [
                # Transfer player to Map 1 at coordinates (5, 5)
                {"code": 201, "parameters": [0, 1, 5, 5]}
            ]
        }]
    }
}
