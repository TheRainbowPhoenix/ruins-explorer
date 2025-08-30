HEADER = {
    'description': 'Map Data',
    'exports': ["displayName", "tilesetId", "width", "height", "scrollType", "specifyBattleback", "data", "events"],
}

displayName = "Hunt Ground"
tilesetId = "jrpg" # Corresponds to the key in AssetManager
width = 32
height = 24
scrollType = 0
specifyBattleback = False

data = [
    3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3,
    3, 3, 2, 2, 1, 3, 3, 3, 1, 1, 3, 1, 1, 3, 3, 3, 3, 1, 1, 1, 1, 1, 1, 2, 2, 3, 3, 2, 3, 3, 3, 3,
    3, 3, 2, 2, 3, 3, 1, 1, 5, 5, 5, 5, 1, 1, 3, 3, 3, 1, 1, 1, 1, 5, 1, 1, 1, 1, 1, 1, 3, 3, 2, 3,
    3, 2, 2, 1, 3, 1, 5, 5, 5, 5, 5, 5, 5, 1, 3, 3, 3, 1, 1, 3, 3, 3, 3, 1, 1, 1, 5, 5, 1, 1, 1, 3,
    3, 1, 1, 1, 5, 1, 1, 5, 5, 5, 5, 5, 5, 1, 1, 1, 1, 1, 2, 2, 2, 1, 3, 3, 1, 5, 5, 5, 5, 1, 1, 3,
    3, 1, 1, 5, 1, 1, 1, 1, 5, 5, 5, 5, 1, 1, 3, 3, 3, 2, 2, 2, 1, 1, 1, 3, 3, 1, 1, 5, 1, 1, 3, 3,
    3, 2, 1, 1, 1, 1, 1, 1, 3, 3, 1, 2, 2, 1, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 1, 1, 1, 1, 3, 3, 3,
    3, 2, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 1, 1, 1, 1, 1, 3, 3, 3, 3, 3,
    3, 2, 2, 1, 1, 1, 3, 3, 2, 2, 2, 2, 3, 3, 3, 3, 3, 2, 2, 3, 3, 1, 1, 3, 1, 1, 2, 2, 2, 2, 1, 3,
    3, 2, 2, 2, 1, 1, 1, 3, 3, 2, 2, 3, 3, 1, 1, 1, 1, 1, 1, 2, 3, 1, 1, 3, 3, 2, 2, 2, 2, 2, 3, 3,
    3, 2, 2, 3, 3, 1, 1, 1, 3, 3, 3, 3, 1, 1, 1, 3, 3, 1, 1, 2, 3, 5, 1, 1, 3, 2, 2, 2, 2, 3, 3, 3,
    3, 3, 3, 3, 1, 1, 1, 2, 1, 3, 3, 1, 1, 1, 3, 3, 3, 1, 1, 3, 3, 1, 5, 1, 3, 3, 3, 3, 3, 3, 3, 3,
    3, 1, 1, 1, 1, 1, 1, 2, 2, 1, 3, 2, 1, 3, 3, 3, 3, 1, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 3,
    3, 1, 1, 1, 3, 1, 1, 2, 2, 1, 3, 2, 1, 1, 3, 3, 3, 1, 3, 3, 3, 3, 1, 1, 1, 1, 1, 5, 1, 2, 3, 3,
    3, 1, 1, 3, 3, 1, 1, 1, 1, 3, 3, 3, 1, 1, 3, 3, 3, 1, 3, 3, 3, 3, 3, 3, 3, 3, 1, 5, 1, 3, 3, 3,
    3, 3, 3, 3, 1, 5, 1, 1, 3, 3, 2, 3, 3, 1, 1, 3, 3, 5, 5, 1, 1, 1, 3, 3, 1, 3, 3, 1, 5, 1, 2, 3,
    3, 3, 1, 1, 1, 5, 1, 3, 3, 2, 1, 1, 3, 1, 1, 3, 3, 1, 1, 5, 3, 3, 3, 1, 1, 1, 3, 3, 1, 1, 2, 3,
    3, 1, 5, 1, 1, 1, 1, 3, 3, 2, 1, 1, 1, 5, 1, 3, 3, 3, 1, 1, 1, 1, 1, 1, 5, 1, 1, 3, 1, 1, 1, 3,
    3, 1, 1, 3, 1, 1, 1, 1, 3, 3, 1, 1, 5, 1, 1, 3, 3, 3, 3, 1, 1, 1, 5, 5, 1, 1, 1, 3, 3, 1, 3, 3,
    3, 1, 3, 3, 3, 3, 3, 3, 3, 1, 1, 1, 3, 3, 1, 3, 3, 2, 1, 1, 5, 1, 1, 1, 1, 3, 1, 1, 3, 1, 3, 3,
    3, 1, 3, 3, 1, 2, 3, 2, 3, 3, 1, 1, 1, 3, 3, 3, 3, 1, 1, 5, 2, 3, 3, 3, 3, 3, 1, 1, 3, 1, 1, 3,
    3, 1, 1, 1, 1, 1, 1, 2, 3, 3, 2, 1, 3, 3, 3, 3, 3, 1, 1, 1, 2, 3, 3, 3, 2, 2, 1, 1, 1, 5, 1, 3,
    3, 3, 3, 1, 1, 1, 1, 1, 3, 3, 2, 1, 1, 1, 2, 3, 3, 8, 6, 8, 3, 3, 1, 1, 2, 2, 2, 1, 1, 1, 3, 3,
    3, 3, 3, 3, 3, 3, 8, 6, 3, 3, 3, 3, 8, 4, 3, 3, 3, 3, 6, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3
]

events = {
    # Event at (x=29, y=4)
    (29, 4): { # Event ID 1
        "id": 1,
        "name": "Event 1",
        "x": 29, "y": 4,
        "pages": [
            {
                "graphic": {"tileId":7},
                "through": False,
                "list": [

                ]
            }
        ]
    },

    # Event at (x=9, y=3)
    (9, 3): { # Event ID 2
        "id": 2,
        "name": "Event 2",
        "x": 9, "y": 3,
        "pages": [
            {
                "graphic": {"tileId":55},
                "through": False,
                "list": [

                ]
            }
        ]
    },

    # Event at (x=18, y=9)
    (18, 9): { # Event ID 3
        "id": 3,
        "name": "Event 3",
        "x": 18, "y": 9,
        "pages": [
            {
                "graphic": {"tileId":55},
                "through": False,
                "list": [

                ]
            }
        ]
    },

    # Event at (x=12, y=22)
    (12, 22): { # Event ID 4
        "id": 4,
        "name": "Vorpal",
        "x": 12, "y": 22,
        "pages": [
            {
                "graphic": {"tileId":55},
                "through": False,
                "list": [
                    {"code": 101, "parameters": ["ylva_shocked",0,0,2], "indent": 0},
                    {"code": 401, "parameters": ["C'est un gros lapin"], "indent": 0},
                    {"code": 401, "parameters": ["Tu es sur de l'affronter ?"], "indent": 0},
                    {"code": 102, "parameters": [["Non ! Fuir","Oui ! Bagarre !"],0,10], "indent": 0},
                    {"code": 111, "parameters": [1,10,0,2,0,0], "indent": 0},
                        {"code": 301, "parameters": [0,5,True,True,10], "indent": 1},
                    {"code": 412, "parameters": [], "indent": 0}
                ]
            }
        ]
    },

    # Event at (x=18, y=21)
    (18, 21): { # Event ID 5
        "id": 5,
        "name": "Event 5",
        "x": 18, "y": 21,
        "pages": [
            {
                "graphic": {"tileId":55},
                "through": False,
                "list": [

                ]
            }
        ]
    },

    # Event at (x=2, y=13)
    (2, 13): { # Event ID 6
        "id": 6,
        "name": "Cabbit",
        "x": 2, "y": 13,
        "pages": [
            {
                "graphic": {"tileId":55},
                "through": False,
                "list": [
                    {"code": 101, "parameters": ["",0,0,2], "indent": 0},
                    {"code": 401, "parameters": ["Before battle"], "indent": 0},
                    {"code": 301, "parameters": [0,4,True,True,10], "indent": 0},
                    {"code": 111, "parameters": [1,10,0,1,0,0], "indent": 0},
                        {"code": 101, "parameters": ["",0,0,2], "indent": 1},
                        {"code": 401, "parameters": ["Heh what ?"], "indent": 1},
                        {"code": 401, "parameters": ["Eeek !"], "indent": 1},
                    {"code": 412, "parameters": [], "indent": 0},
                    {"code": 111, "parameters": [1,10,0,2,0,0], "indent": 0},
                        {"code": 101, "parameters": ["",0,0,2], "indent": 1},
                        {"code": 401, "parameters": ["Trying to run away, huh ?"], "indent": 1},
                    {"code": 412, "parameters": [], "indent": 0},
                    {"code": 111, "parameters": [1,10,0,3,0,0], "indent": 0},
                        {"code": 101, "parameters": ["",0,0,2], "indent": 1},
                        {"code": 401, "parameters": ["Hah!"], "indent": 1},
                        {"code": 401, "parameters": ["You're still too weak."], "indent": 1},
                    {"code": 412, "parameters": [], "indent": 0}
                ]
            }
        ]
    },

    # Event at (x=2, y=2)
    (2, 2): { # Event ID 7
        "id": 7,
        "name": "Event 7",
        "x": 2, "y": 2,
        "pages": [
            {
                "graphic": {"tileId":55},
                "through": False,
                "list": [

                ]
            }
        ]
    },

    # Event at (x=22, y=22)
    (22, 22): { # Event ID 8
        "id": 8,
        "name": "Event 8",
        "x": 22, "y": 22,
        "pages": [
            {
                "graphic": {"tileId":55},
                "through": False,
                "list": [

                ]
            }
        ]
    },

    # Event at (x=21, y=5)
    (21, 5): { # Event ID 9
        "id": 9,
        "name": "Event 9",
        "x": 21, "y": 5,
        "pages": [
            {
                "graphic": {"tileId":55},
                "through": False,
                "list": [

                ]
            }
        ]
    },

    # Event at (x=22, y=5)
    (22, 5): { # Event ID 10
        "id": 10,
        "name": "Event 10",
        "x": 22, "y": 5,
        "pages": [
            {
                "graphic": {"tileId":55},
                "through": False,
                "list": [

                ]
            }
        ]
    },

    # Event at (x=30, y=4)
    (30, 4): { # Event ID 11
        "id": 11,
        "name": "Event 11",
        "x": 30, "y": 4,
        "pages": [
            {
                "graphic": {"tileId":55},
                "through": False,
                "list": [

                ]
            }
        ]
    },

    # Event at (x=24, y=15)
    (24, 15): { # Event ID 12
        "id": 12,
        "name": "Event 12",
        "x": 24, "y": 15,
        "pages": [
            {
                "graphic": {"tileId":4},
                "through": False,
                "list": [

                ]
            }
        ]
    },

    # Event at (x=13, y=3)
    (13, 3): { # Event ID 13
        "id": 13,
        "name": "Event 13",
        "x": 13, "y": 3,
        "pages": [
            {
                "graphic": {"tileId":4},
                "through": False,
                "list": [

                ]
            }
        ]
    },

    # Event at (x=29, y=3)
    (29, 3): { # Event ID 14
        "id": 14,
        "name": "Event 14",
        "x": 29, "y": 3,
        "pages": [
            {
                "graphic": {"tileId":26},
                "through": False,
                "list": [

                ]
            }
        ]
    },

    # Event at (x=10, y=17)
    (10, 17): { # Event ID 15
        "id": 15,
        "name": "Event 15",
        "x": 10, "y": 17,
        "pages": [
            {
                "graphic": {"tileId":55},
                "through": False,
                "list": [

                ]
            }
        ]
    },

    # Event at (x=10, y=16)
    (10, 16): { # Event ID 16
        "id": 16,
        "name": "Event 16",
        "x": 10, "y": 16,
        "pages": [
            {
                "graphic": {"tileId":55},
                "through": False,
                "list": [

                ]
            }
        ]
    },

    # Event at (x=7, y=23)
    (7, 23): { # Event ID 17
        "id": 17,
        "name": "Ylva",
        "x": 7, "y": 23,
        "pages": [
            {
                "graphic": {"tileId":97},
                "through": False,
                "list": [
                    {"code": 101, "parameters": ["ylva_angry",0,0,2], "indent": 0},
                    {"code": 401, "parameters": ["Oh non, non, non."], "indent": 0},
                    {"code": 401, "parameters": ["Tu crois que c'est fini ?"], "indent": 0},
                    {"code": 401, "parameters": [""], "indent": 0},
                    {"code": 101, "parameters": ["ylva_happy",0,0,2], "indent": 0},
                    {"code": 401, "parameters": ["Je t'ai laisse sortir"], "indent": 0},
                    {"code": 401, "parameters": ["pour chasser, pas pour"], "indent": 0},
                    {"code": 401, "parameters": ["flaner dans les fleurs! "], "indent": 0},
                    {"code": 101, "parameters": ["ylva_ok",0,0,2], "indent": 0},
                    {"code": 401, "parameters": ["Cinq lapins."], "indent": 0},
                    {"code": 401, "parameters": ["Apporte-m'en cinq."], "indent": 0},
                    {"code": 101, "parameters": ["",0,0,2], "indent": 0},
                    {"code": 401, "parameters": ["*Ylva bloque le chemin"], "indent": 0},
                    {"code": 401, "parameters": ["du retour.*"], "indent": 0},
                    {"code": 101, "parameters": ["",0,0,2], "indent": 0},
                    {"code": 401, "parameters": ["Objectif :"], "indent": 0},
                    {"code": 401, "parameters": ["Chasser 5 lapins"], "indent": 0}
                ]
            },
            {
                "conditions": {"switch1Valid": False, "switch2Valid": False, "variableValid": True, "selfSwitchValid": False, "variableId": 9, "variableValue": 5},
                "graphic": {"tileId":0},
                "through": False,
                "list": [
                    {"code": 101, "parameters": ["ylva_ok",0,0,2], "indent": 0},
                    {"code": 401, "parameters": ["Hmm... Pas totalement"], "indent": 0},
                    {"code": 401, "parameters": ["inefficace. Pour un humain."], "indent": 0},
                    {"code": 101, "parameters": ["",0,0,2], "indent": 0},
                    {"code": 401, "parameters": ["...Merci ?"], "indent": 0},
                    {"code": 101, "parameters": ["ylva_happy",0,0,2], "indent": 0},
                    {"code": 401, "parameters": ["Tiens, en fouillant les"], "indent": 0},
                    {"code": 401, "parameters": ["feuilles pour toi, j'ai"], "indent": 0},
                    {"code": 401, "parameters": ["trouve ça."], "indent": 0},
                    {"code": 101, "parameters": ["",0,0,2], "indent": 0},
                    {"code": 401, "parameters": ["*Ylva te tend"], "indent": 0},
                    {"code": 401, "parameters": ["d'etranges grains.*"], "indent": 0},
                    {"code": 101, "parameters": ["ylva_ok",0,0,2], "indent": 0},
                    {"code": 401, "parameters": ["On dirait des graines..."], "indent": 0},
                    {"code": 401, "parameters": ["bizarres. Tu devrais"], "indent": 0},
                    {"code": 401, "parameters": ["les planter, pour voir ?"], "indent": 0},
                    {"code": 126, "parameters": [10,0,0,1], "indent": 0},
                    {"code": 101, "parameters": ["ylva_angry",0,0,2], "indent": 0},
                    {"code": 401, "parameters": ["MAIS D'ABORD !"], "indent": 0},
                    {"code": 401, "parameters": ["Cinq autres lapins !"], "indent": 0},
                    {"code": 401, "parameters": ["La faim tenaille !"], "indent": 0},
                    {"code": 101, "parameters": ["",0,0,2], "indent": 0},
                    {"code": 401, "parameters": ["Objectif :"], "indent": 0},
                    {"code": 401, "parameters": ["Chasser 5 lapins"], "indent": 0},
                    {"code": 401, "parameters": ["de plus (10/12)"], "indent": 0}
                ]
            },
            {
                "conditions": {"switch1Valid": False, "switch2Valid": False, "variableValid": True, "variableId": 9, "variableValue": 10, "selfSwitchValid": False},
                "graphic": {"tileId":0},
                "through": False,
                "list": [
                    {"code": 101, "parameters": ["ylva_ok",0,0,2], "indent": 0},
                    {"code": 401, "parameters": ["La harde faiblit !"], "indent": 0},
                    {"code": 401, "parameters": ["J'en veux encore deux."], "indent": 0},
                    {"code": 101, "parameters": ["ylva_happy",0,0,2], "indent": 0},
                    {"code": 401, "parameters": ["Les deux plus dodus,"], "indent": 0},
                    {"code": 401, "parameters": ["bien sur."], "indent": 0},
                    {"code": 101, "parameters": ["",0,0,2], "indent": 0},
                    {"code": 401, "parameters": ["...Ils ont tous"], "indent": 0},
                    {"code": 401, "parameters": ["la même taille."], "indent": 0},
                    {"code": 101, "parameters": ["ylva_ok",0,0,2], "indent": 0},
                    {"code": 401, "parameters": ["Alors trouve les deux"], "indent": 0},
                    {"code": 401, "parameters": ["qui *ont l'air* les"], "indent": 0},
                    {"code": 401, "parameters": ["plus dodus."], "indent": 0},
                    {"code": 101, "parameters": ["",0,0,2], "indent": 0},
                    {"code": 401, "parameters": ["Objectif :"], "indent": 0},
                    {"code": 401, "parameters": ["Chasser 2 derniers lapins"], "indent": 0}
                ]
            }
        ]
    }
}