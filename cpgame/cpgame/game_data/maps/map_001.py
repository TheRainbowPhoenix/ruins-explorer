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
            "graphic": {"tileId": 55, "direction": 2},
            "list": [
                {"code": 101, "parameters": []}, # Show Text
                {"code": 401, "parameters": ["Arion: Greetings, traveler."]},
                {"code": 401, "parameters": ["Have you seen the crystal?"]},
                {"code": 401, "parameters": ["The crystal is over there."]},
                # Set Variable #42 to the value 4
                {"code": 401, "parameters": ["The secret answer was \\V[42]."]},
                {"code": 122, "parameters": [42, 42, 0, 0, 42]}, 
                # Show Text command
                {"code": 101, "parameters": []},
                # Text lines with control codes
                {"code": 401, "parameters": ["Ah, \\N[1]! Your HP is \\HP[1]."]},
                {"code": 401, "parameters": ["The secret answer is now \\V[42]."]},
                {"code": 401, "parameters": ["Please enter a new secret"]},
                {"code": 103, "parameters": [42, 3]},
                {"code": 101, "parameters": []}, # Show Text
                {"code": 401, "parameters": ["The secret answer is now \\V[42]."]},
                {"code": 303, "parameters": [1, 10]},
                {"code": 101, "parameters": []}, # Show Text
                {"code": 401, "parameters": ["The name is now \\N[1]."]}
            ]
        }, { # Page 2: Shows if Switch 25 is ON
            "conditions": {"switch1Id": 25, "switch1Valid": True},
            "graphic": {"tileId": 81, "direction": 2},
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
            "graphic": {"tileId": 53},
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
            "graphic": {"tileId": 4},
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
                {"code": 101, "parameters":["",0,0,2]},
                {"code": 401, "parameters": ["The crystal hums. Power level: \\V[1]"]}
            ]
        }]
    },
    (9,9): { # Event ID 4: A Farm Plot
        "id": 4, "name": "FarmPlot", "x": 9, "y": 9,
        "pages": [
            { # PAGE 1: Untilled Soil (Default)
                "conditions": {},
                "graphic": {"tileId": 94}, # Normal soil graphic
                "through": True,
                "list": [
                    {"code": 101}, {"code": 401, "parameters": ["PAGE 1: Untilled Soil (Default)"]},
                    {"code": 356, "parameters": ["check_soil(4)"]}
                ]
            },
            { # PAGE 2: Tilled Soil
                "conditions": {"selfSwitchCh": "A", "selfSwitchValid": True},
                "graphic": {"tileId": 95}, # Tilled soil graphic
                "through": True,
                "list": [
                    {"code": 101}, {"code": 401, "parameters": ["PAGE 2: Tilled Soil"]},
                    {"code": 356, "parameters": ["check_soil(4)"]},
                    {"code": 111, "parameters": [1, 10, 0, 1, 0]},
                        {"code": 101, "indent": 1}, {"code": 401, "indent": 1, "parameters": ["You planted a potato seed."]},
                        {"code": 123, "indent": 1, "parameters": ["B", 0]}, # Turn Self Switch 'B' ON
                        {"code": 356, "indent": 1, "parameters": ["start_growth(4, 'potato', 20)"]}, # New plugin command
                    {"code": 412}, # End If
                    # If Variable #10 == 2 (Corn)...
                    {"code": 111, "parameters": [1, 10, 0, 2, 0]},
                        {"code": 101, "indent": 1}, {"code": 401, "indent": 1, "parameters": ["You planted a corn seed."]},
                        {"code": 123, "indent": 1, "parameters": ["B", 0]},
                        {"code": 356, "indent": 1, "parameters": ["start_growth(4, 'corn', 45)"]},
                    {"code": 412}, # End If
                ]
            },
            { # PAGE 3: Growing
                "conditions": {"selfSwitchCh": "B", "selfSwitchValid": True},
                "graphic": {"tileId": 100}, # Sprout graphic
                "through": True,
                "list": [
                    {"code": 101}, {"code": 401, "parameters": ["PAGE 3: Growing"]},
                    {"code": 356, "parameters": ["check_soil(4)"]}
                ]
            },
            { # PAGE 4: Harvestable (Highest Priority)
                "conditions": {"selfSwitchCh": "D", "selfSwitchValid": True},
                "graphic": {"tileId": 96}, # Ripe plant graphic
                "through": True,
                "list": [
                    {"code": 101}, {"code": 401, "parameters": ["PAGE 4: Harvestable"]},
                    {"code": 356, "parameters": ["check_soil(4)"]}
                ]
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
    },
    (7, 9): { # Event ID 4: A Farm Plot
        "id": 5, "name": "FarmPlot", "x": 8, "y": 9,
        "pages": [
            { # PAGE 1: Untilled Soil (Default Page)
                "conditions": {},
                "graphic": {"tileId": 40}, # Normal soil graphic
                "list": [
                    {"code": 101, "parameters": []}, 
                    {"code": 401, "parameters": ["What will you plant?"]},
                    {"code": 102, "parameters": [["Potato", "Corn", "Cancel"], 2, 10]}, # Show Choices, store result in Var 10

                    {"code": 101, "indent": 0}, {"code": 401, "indent": 0, "parameters": ["What will you plant (2)?"]},
                    
                    {"code": 402, "indent": 0, "parameters": [0]}, # When [Potato]
                        {"code": 101, "indent": 1}, {"code": 401, "indent": 1, "parameters": ["When Potato."]},
                        # {"code": 356, "indent": 1, "parameters": ["start_growth(4, 'potato', 20)"]},
                    {"code": 412, "indent": 0}, # End When
                    
                    {"code": 402, "indent": 0, "parameters": [1]}, # When [Corn]
                        {"code": 101, "indent": 1}, {"code": 401, "indent": 1, "parameters": ["When Corn."]},
                        # {"code": 356, "indent": 1, "parameters": ["start_growth(4, 'potato', 20)"]},
                    {"code": 412, "indent": 0}, # End When

                    {"code": 402, "indent": 0, "parameters": [2]}, # When [**]
                        {"code": 101, "indent": 1}, {"code": 401, "indent": 1, "parameters": ["No choice was made."]},
                        # {"code": 356, "indent": 1, "parameters": ["start_growth(4, 'corn', 45)"]},
                    {"code": 412, "indent": 0}, # End When

                    {"code": 101, "parameters":["",0,0,2]},
                    {"code": 401, "parameters": ["Choice ID: \\V[10]"]},

                    {"code": 111, "indent": 0, "parameters": [1, 10, 0, 1, 0]}, # If Var 10 == 1 (Potato was chosen)
                        {"code": 101, "indent": 1}, {"code": 401, "indent": 1, "parameters": ["It's potato."]},
                        {"code": 123, "indent": 1, "parameters": ["B", 0]},
                    {"code": 412}, # End If

                    {"code": 111, "indent": 0, "parameters": [1, 10, 0, 2, 0]}, # If Var 10 == 2 (Corn was chosen)
                        {"code": 101, "indent": 1}, {"code": 401, "indent": 1, "parameters": ["It's corn."]},
                        {"code": 123, "indent": 1, "parameters": ["B", 0]},
                    {"code": 412}, # End If

                    {"code": 111, "indent": 0, "parameters": [1, 10, 0, 3, 0]}, # If Var 10 == 3 (Cancel)
                        {"code": 101, "indent": 1}, {"code": 401, "indent": 1, "parameters": ["Nothing for today, heh ?"]},
                        {"code": 123, "indent": 1, "parameters": ["B", 0]},
                    {"code": 412}, # End If
                    {"code": 0}
                ]
            }
        ]
    },
    (1,1): { # Event ID 5: Shopkeeper
        "id": 5, "name": "Shopkeeper", "x": 1, "y": 1,
        "pages": [{
            "graphic": {"tileId": 57},
            "list": [
                {"code": 101}, {"code": 401, "parameters": ["Welcome! Care to browse my wares?"]},
                # Shop command. Params: [item_type, item_id, price_type, price, purchase_only]
                # price_type 0 = standard, 1 = override
                {"code": 302, "parameters": [0, 5, 0, 0, False]}, # Item 5 (Potato Seed)
                {"code": 605, "parameters": [0, 6, 1, 150, 0]}, # Item 6 (Corn Seed), price override 150G
                {"code": 605, "parameters": [1, 2, 0, 0, 0]},   # Weapon 2 (Axe)
            ]
        }]
    }
}
