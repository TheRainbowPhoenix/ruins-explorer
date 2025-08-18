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
    (3, 3): { # Event ID 1
        "id": 1,
        "name": "ActorNPC",
        "x": 3, "y": 3,
        "pages": [{
            "graphic": {"tileId": 56, "direction": 2},
            "list": [
                {"code": 101, "parameters": []}, # Show Text
                {"code": 401, "parameters": ["Arion: Greetings, traveler."]},
                {"code": 401, "parameters": ["The crystal is over there."]}
            ]
        }]
    },
    # Event at (x=6, y=6)
    (6, 6): {
        "id": 2, "name": "Crystal", "x": 6, "y": 6,
        "pages": [{
            "graphic": {"tileId": 52},
            "list": [
                {"code": 101, "parameters": []},
                {"code": 401, "parameters": ["A strange, glowing crystal..."]}
            ]
        }]
    },
    # Event at (x=10, y=2) - Teleport to Map 2
    (10, 2): {
        "id": 3, "name": "Portal", "x": 10, "y": 2,
        "pages": [{
            "graphic": {"tileId": 60},
            "list": [
                # Transfer player to Map 2 at coordinates (5, 5)
                {"code": 201, "parameters": [0, 2, 5, 5]}
            ]
        }]
    }
}
