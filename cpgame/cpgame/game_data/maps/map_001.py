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
    },
    (9,9): { # Event ID 4: A Farm Plot
        "id": 4, "name": "FarmPlot", "x": 9, "y": 9,
        "pages": [
            { # PAGE 4: Harvestable (Highest Priority)
                "conditions": {"selfSwitchCh": "D", "selfSwitchValid": True},
                "graphic": {"tileId": 43}, # Ripe plant graphic
                "list": [{"code": 356, "parameters": ["check_soil(4)"]}]
            },
            { # PAGE 3: Growing
                "conditions": {"selfSwitchCh": "B", "selfSwitchValid": True},
                "graphic": {"tileId": 42}, # Sprout graphic
                "list": [{"code": 356, "parameters": ["check_soil(4)"]}]
            },
            { # PAGE 2: Tilled Soil
                "conditions": {"selfSwitchCh": "A", "selfSwitchValid": True},
                "graphic": {"tileId": 41}, # Tilled soil graphic
                "list": [{"code": 356, "parameters": ["check_soil(4)"]}]
            },
            { # PAGE 1: Untilled Soil (Default)
                "conditions": {},
                "graphic": {"tileId": 40}, # Normal soil graphic
                "list": [{"code": 356, "parameters": ["check_soil(4)"]}]
            }
        ]
    },
    (8, 9): { # Event ID 4: A Farm Plot
        "id": 5, "name": "FarmPlot", "x": 8, "y": 9,
        "pages": [
            { # PAGE 1: Untilled Soil (Default Page)
                "conditions": {},
                "graphic": {"tileId": 40}, # Normal soil graphic
                "list": [
                    {"code": 101}, {"code": 401, "parameters": ["It's a patch of fertile soil."]},
                    # On interaction, "till" the soil
                    {"code": 123, "parameters": ["A", 0]} # Turn Self Switch 'A' ON
                ]
            }, { # PAGE 2: Tilled Soil (Condition: Self Switch 'A' is ON)
                "conditions": {"selfSwitchCh": "A", "selfSwitchValid": True},
                "graphic": {"tileId": 41}, # Tilled soil graphic
                "list": [
                    # If player has Potato Seeds (item ID 5)...
                    {"code": 111, "parameters": ["item", 5]}, # Placeholder for item condition
                        # ...then plant them.
                        {"code": 126, "parameters": [5, 1, 1]}, # Remove 1 potato seed
                        {"code": 101,"indent":1}, {"code": 401,"indent":1, "parameters": ["You planted the seeds."]},
                        {"code": 123,"indent":1, "parameters": ["B", 0]}, # Turn Self Switch 'B' ON
                    {"code": 411}, # Else...
                        {"code": 101,"indent":1}, {"code": 401,"indent":1, "parameters": ["The soil is ready for planting."]},
                    {"code": 412} # End If
                ]
            }
        ]
    }
}
