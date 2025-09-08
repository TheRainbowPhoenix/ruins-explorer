HEADER = {
    'description': 'Map Data',
    'exports': ["displayName", "tilesetId", "width", "height", "scrollType", "specifyBattleback", "data", "events"],
}

displayName = "Quiet Village"
tilesetId = "riosma_world" # Corresponds to the key in AssetManager
width = 20
height = 8
scrollType = 0
specifyBattleback = False

data = [
    2, 20, 21, 19, 0, 7, 7, 1, 2, 2, 2, 2, 2, 2, 2, 2, 0, 1, 2, 2,
    22, 46, 40, 41, 50, 54, 50, 51, 1, 2, 0, 1, 2, 2, 2, 0, 48, 49, 17, 17,
    42, 42, 56, 57, 46, 46, 46, 47, 74, 74, 74, 74, 74, 74, 74, 74, 45, 46, 46, 46,
    58, 58, 72, 73, 9, 8, 44, 75, 71, 3, 3, 3, 3, 3, 3, 64, 12, 13, 46, 46,
    8, 44, 8, 8, 25, 59, 59, 59, 47, 3, 68, 69, 67, 3, 64, 9, 28, 29, 8, 8,
    40, 41, 46, 42, 42, 9, 8, 8, 11, 3, 27, 44, 11, 3, 27, 25, 46, 40, 41, 42,
    56, 57, 42, 43, 58, 75, 46, 46, 63, 3, 61, 62, 63, 3, 45, 46, 42, 56, 57, 43,
    72, 73, 58, 58, 46, 46, 46, 47, 95, 3, 93, 94, 95, 3, 61, 46, 58, 72, 73, 58
]

events = {
    # Event at (x=1, y=4)
    (1, 4): { # Event ID 1
        "id": 1,
        "name": "Level 1",
        "x": 1, "y": 4,
        "pages": [
            {
                "graphic": {"tileId":60},
                "through": False,
                "list": [
                    {"code": 123, "parameters": ["A",0], "indent": 0}
                ]
            },
            {
                "conditions": {},
                "graphic": {"tileId":44},
                "through": True,
                "list": [

                ]
            }
        ]
    },

    # Event at (x=6, y=3)
    (6, 3): { # Event ID 2
        "id": 2,
        "name": "Level 2",
        "x": 6, "y": 3,
        "pages": [
            {
                "graphic": {"tileId":60},
                "through": False,
                "list": [
                    {"code": 123, "parameters": ["A",0], "indent": 0}
                ]
            },
            {
                "conditions": {"switch1Valid": False, "switch2Valid": False, "variableValid": False, "selfSwitchValid": True, "selfSwitchCh": "A"},
                "graphic": {"tileId":44},
                "through": True,
                "list": [

                ]
            }
        ]
    },

    # Event at (x=8, y=5)
    (8, 5): { # Event ID 3
        "id": 3,
        "name": "Move",
        "x": 8, "y": 5,
        "pages": [
            {
                "graphic": {"tileId":11},
                "through": True,
                "list": [
                    {"code": 201, "parameters": [0,10,10,5], "indent": 0}
                ]
            }
        ]
    },

    # Event at (x=12, y=5)
    (12, 5): { # Event ID 4
        "id": 4,
        "name": "Move2",
        "x": 12, "y": 5,
        "pages": [
            {
                "graphic": {"tileId":11},
                "through": True,
                "list": [
                    {"code": 201, "parameters": [0,10,14,5], "indent": 0}
                ]
            }
        ]
    },

    # Event at (x=5, y=6)
    (5, 6): { # Event ID 5
        "id": 5,
        "name": "Pipe Out",
        "x": 5, "y": 6,
        "pages": [
            {
                "graphic": {"tileId":75},
                "through": True,
                "list": [
                    {"code": 201, "parameters": [0,10,7,3], "indent": 0}
                ]
            }
        ]
    },

    # Event at (x=7, y=3)
    (7, 3): { # Event ID 6
        "id": 6,
        "name": "Pipe In",
        "x": 7, "y": 3,
        "pages": [
            {
                "graphic": {"tileId":75},
                "through": True,
                "list": [
                    {"code": 201, "parameters": [0,10,5,6], "indent": 0}
                ]
            }
        ]
    },

    # Event at (x=10, y=5)
    (10, 5): { # Event ID 7
        "id": 7,
        "name": "Move Back1",
        "x": 10, "y": 5,
        "pages": [
            {
                "graphic": {"tileId":27},
                "through": True,
                "list": [
                    {"code": 201, "parameters": [0,10,8,5], "indent": 0}
                ]
            }
        ]
    },

    # Event at (x=14, y=5)
    (14, 5): { # Event ID 8
        "id": 8,
        "name": "Move Back2",
        "x": 14, "y": 5,
        "pages": [
            {
                "graphic": {"tileId":27},
                "through": True,
                "list": [
                    {"code": 201, "parameters": [0,10,12,5], "indent": 0}
                ]
            }
        ]
    }
}