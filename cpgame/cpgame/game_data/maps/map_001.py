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
        "pages": [{ # Page 1: Default message
            "graphic": {"tileId": 56, "direction": 2},
            "list": [
                {"code": 101, "parameters": []}, # Show Text
                {"code": 401, "parameters": ["Arion: Greetings, traveler."]},
                {"code": 401, "parameters": ["Have you seen the crystal?"]},
                {"code": 401, "parameters": ["The crystal is over there."]},
                # Set Variable #42 to the value 4
                {"code": 122, "parameters": [42, 42, 0, 0, 4]}, 
                # Show Text command
                {"code": 101, "parameters": []},
                # Text lines with control codes
                {"code": 401, "parameters": ["Ah, \\N[1]! Your HP is \\HP[1]."]},
                {"code": 401, "parameters": ["The secret answer is \\V[42]."]}
            ]
        }, { # Page 2: Shows if Switch 25 is ON
            "conditions": {"switch1Id": 25, "switch1Valid": True},
            "graphic": {"tileId": 57, "direction": 2},
            "list": [
                {"code": 101},
                {"code": 401, "parameters": ["Arion: You touched the crystal!"]},
                {"code": 401, "parameters": ["It has amazing powers."]}
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
                {"code": 401, "parameters": ["A strange, glowing crystal..."]},
                # Set Switch #25 to ON
                {"code": 121, "parameters": [25, 25, 0]}
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
    },

    (8, 1): {
        "id": 3, "name": "Portal", "x": 10, "y": 2,
        "pages": [{
            "graphic": {"tileId": 52},
            "list": [
                # Increment Variable #1 (our cycle counter)
                {"code": 122, "parameters": [1, 1, 1, 0, 1]},
                # Variable #1 %= 8 (so it cycles 0-7)
                {"code": 122, "parameters": [1, 1, 5, 0, 8]},
                # Set Variable #2 = Variable #1
                {"code": 122, "parameters": [2, 2, 0, 1, 1]},
                # Add 40 to Variable #2 to get the final tile ID
                {"code": 122, "parameters": [2, 2, 1, 0, 40]},
                # Change this event's (ID 0) graphic using the value from Variable #2
                {"code": 501, "parameters": [0, 2, True]},
                # Show text displaying the variable
                {"code": 101},
                {"code": 401, "parameters": ["The crystal hums. Power level: \\V[1]"]}
            ]
        }]
    }
}
