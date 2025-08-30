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
        "name": "Flower Cabbit",
        "x": 9, "y": 3,
        "pages": [
            {
                "graphic": {"tileId":55},
                "through": False,
                "list": [
                    {"code": 101, "parameters": ["",0,0,2], "indent": 0},
                    {"code": 401, "parameters": ["Vous etes venu admirer ma"], "indent": 0},
                    {"code": 401, "parameters": ["collection de pissenlits ?"], "indent": 0},
                    {"code": 301, "parameters": [0,4,True,True,10], "indent": 0},
                    {"code": 111, "parameters": [1,10,0,1,0,0], "indent": 0},
                        {"code": 101, "parameters": ["",0,0,2], "indent": 1},
                        {"code": 401, "parameters": ["Non ! Au moins finis..."], "indent": 1},
                        {"code": 401, "parameters": ["au sol... avec.."], "indent": 1},
                        {"code": 401, "parameters": ["mes fleurs..."], "indent": 1},
                        {"code": 122, "parameters": [9,9,1,0,1], "indent": 1},
                        {"code": 123, "parameters": ["A",0], "indent": 1},
                    {"code": 412, "parameters": [], "indent": 0},
                    {"code": 111, "parameters": [1,10,0,2,0,0], "indent": 0},
                        {"code": 101, "parameters": ["",0,0,2], "indent": 1},
                        {"code": 401, "parameters": ["Et n'oublies pas de mettre"], "indent": 1},
                        {"code": 401, "parameters": ["5 etoiles a mon champ de "], "indent": 1},
                        {"code": 401, "parameters": ["fleur sur Lapin-Maps !"], "indent": 1},
                    {"code": 412, "parameters": [], "indent": 0},
                    {"code": 111, "parameters": [1,10,0,3,0,0], "indent": 0},
                        {"code": 101, "parameters": ["",0,0,2], "indent": 1},
                        {"code": 401, "parameters": ["La nature reprend toujours"], "indent": 1},
                        {"code": 401, "parameters": ["ses droits ! "], "indent": 1},
                    {"code": 412, "parameters": [], "indent": 0}
                ]
            },
            {
                "conditions": {"switch1Valid": False, "switch2Valid": False, "variableValid": False, "selfSwitchValid": True, "selfSwitchCh": "A"},
                "graphic": {"tileId":9},
                "through": False,
                "list": [

                ]
            }
        ]
    },

    # Event at (x=18, y=9)
    (18, 9): { # Event ID 3
        "id": 3,
        "name": "Chill Cabbit",
        "x": 18, "y": 9,
        "pages": [
            {
                "graphic": {"tileId":55},
                "through": False,
                "list": [
                    {"code": 101, "parameters": ["",0,0,2], "indent": 0},
                    {"code": 401, "parameters": ["Oh bonjour!"], "indent": 0},
                    {"code": 401, "parameters": ["Je n'ai plus de carottes"], "indent": 0},
                    {"code": 401, "parameters": ["a t'offrir... "], "indent": 0},
                    {"code": 301, "parameters": [0,4,True,True,10], "indent": 0},
                    {"code": 111, "parameters": [1,10,0,1,0,0], "indent": 0},
                        {"code": 101, "parameters": ["",0,0,2], "indent": 1},
                        {"code": 401, "parameters": ["Je- rends l'ame..."], "indent": 1},
                        {"code": 122, "parameters": [9,9,1,0,1], "indent": 1},
                        {"code": 123, "parameters": ["A",0], "indent": 1},
                    {"code": 412, "parameters": [], "indent": 0},
                    {"code": 111, "parameters": [1,10,0,2,0,0], "indent": 0},
                        {"code": 101, "parameters": ["",0,0,2], "indent": 1},
                        {"code": 401, "parameters": ["He, tu me fais de l'ombre !"], "indent": 1},
                    {"code": 412, "parameters": [], "indent": 0},
                    {"code": 111, "parameters": [1,10,0,3,0,0], "indent": 0},
                        {"code": 101, "parameters": ["",0,0,2], "indent": 1},
                        {"code": 401, "parameters": ["Le calme... maintenant..."], "indent": 1},
                        {"code": 401, "parameters": ["Mes carottes !"], "indent": 1},
                    {"code": 412, "parameters": [], "indent": 0}
                ]
            },
            {
                "conditions": {"switch1Valid": False, "switch2Valid": False, "variableValid": False, "selfSwitchValid": True, "selfSwitchCh": "A"},
                "graphic": {"tileId":9},
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
        "name": "Vor-re-pal",
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
                    {"code": 401, "parameters": ["Heu. Bonjour. Vous ne"], "indent": 0},
                    {"code": 401, "parameters": ["savez pas ou se cache"], "indent": 0},
                    {"code": 401, "parameters": ["Ylva ? Je veux la fuir"], "indent": 0},
                    {"code": 301, "parameters": [0,4,True,True,10], "indent": 0},
                    {"code": 111, "parameters": [1,10,0,1,0,0], "indent": 0},
                        {"code": 101, "parameters": ["",0,0,2], "indent": 1},
                        {"code": 401, "parameters": ["Premiere sortie..."], "indent": 1},
                        {"code": 401, "parameters": ["et je me fais..."], "indent": 1},
                        {"code": 401, "parameters": ["devorer..."], "indent": 1},
                        {"code": 122, "parameters": [9,9,1,0,1], "indent": 1},
                        {"code": 123, "parameters": ["A",0], "indent": 1},
                    {"code": 412, "parameters": [], "indent": 0},
                    {"code": 111, "parameters": [1,10,0,2,0,0], "indent": 0},
                        {"code": 101, "parameters": ["",0,0,2], "indent": 1},
                        {"code": 401, "parameters": ["Attendez ! Vous avez"], "indent": 1},
                        {"code": 401, "parameters": ["au moins un indice non ? "], "indent": 1},
                    {"code": 412, "parameters": [], "indent": 0},
                    {"code": 111, "parameters": [1,10,0,3,0,0], "indent": 0},
                        {"code": 101, "parameters": ["",0,0,2], "indent": 1},
                        {"code": 401, "parameters": ["Bon. Apparemment, je"], "indent": 1},
                        {"code": 401, "parameters": ["suis bien cache ici..."], "indent": 1},
                    {"code": 412, "parameters": [], "indent": 0}
                ]
            },
            {
                "conditions": {"switch1Valid": False, "switch2Valid": False, "variableValid": False, "selfSwitchValid": True, "selfSwitchCh": "A"},
                "graphic": {"tileId":9},
                "through": False,
                "list": [

                ]
            }
        ]
    },

    # Event at (x=2, y=2)
    (2, 2): { # Event ID 7
        "id": 7,
        "name": "Grass Cabit",
        "x": 2, "y": 2,
        "pages": [
            {
                "graphic": {"tileId":55},
                "through": False,
                "list": [
                    {"code": 101, "parameters": ["",0,0,2], "indent": 0},
                    {"code": 401, "parameters": ["Ssshhh ! Tu fais fuir"], "indent": 0},
                    {"code": 401, "parameters": ["les bonnes herbes !"], "indent": 0},
                    {"code": 301, "parameters": [0,4,True,True,10], "indent": 0},
                    {"code": 111, "parameters": [1,10,0,1,0,0], "indent": 0},
                        {"code": 101, "parameters": ["",0,0,2], "indent": 1},
                        {"code": 401, "parameters": ["Glurb !"], "indent": 1},
                        {"code": 401, "parameters": ["J'aurais du me cacher..."], "indent": 1},
                        {"code": 401, "parameters": ["dans les plus hautes herbes"], "indent": 1},
                        {"code": 122, "parameters": [9,9,1,0,1], "indent": 1},
                        {"code": 123, "parameters": ["A",0], "indent": 1},
                    {"code": 412, "parameters": [], "indent": 0},
                    {"code": 111, "parameters": [1,10,0,2,0,0], "indent": 0},
                        {"code": 101, "parameters": ["",0,0,2], "indent": 1},
                        {"code": 401, "parameters": ["Reviens te battre,"], "indent": 1},
                        {"code": 401, "parameters": ["espece de mauviette !"], "indent": 1},
                    {"code": 412, "parameters": [], "indent": 0},
                    {"code": 111, "parameters": [1,10,0,3,0,0], "indent": 0},
                        {"code": 101, "parameters": ["",0,0,2], "indent": 1},
                        {"code": 401, "parameters": ["Hah!"], "indent": 1},
                        {"code": 401, "parameters": ["Pas fameux comme chasseur !"], "indent": 1},
                    {"code": 412, "parameters": [], "indent": 0}
                ]
            },
            {
                "conditions": {"switch1Valid": False, "switch2Valid": False, "variableValid": False, "selfSwitchValid": True, "selfSwitchCh": "A"},
                "graphic": {"tileId":9},
                "through": False,
                "list": [

                ]
            }
        ]
    },

    # Event at (x=22, y=22)
    (22, 22): { # Event ID 8
        "id": 8,
        "name": "Tree Cabbit",
        "x": 22, "y": 22,
        "pages": [
            {
                "graphic": {"tileId":55},
                "through": False,
                "list": [
                    {"code": 101, "parameters": ["",0,0,2], "indent": 0},
                    {"code": 401, "parameters": ["Je suis un la- PIN !"], "indent": 0},
                    {"code": 401, "parameters": ["Je suis un PIN !"], "indent": 0},
                    {"code": 401, "parameters": ["Il n'y a rien a manger ici"], "indent": 0},
                    {"code": 301, "parameters": [0,4,True,True,10], "indent": 0},
                    {"code": 111, "parameters": [1,10,0,1,0,0], "indent": 0},
                        {"code": 101, "parameters": ["",0,0,2], "indent": 1},
                        {"code": 401, "parameters": ["TIIIIMBEEEER !"], "indent": 1},
                        {"code": 401, "parameters": [""], "indent": 1},
                        {"code": 122, "parameters": [9,9,1,0,1], "indent": 1},
                        {"code": 123, "parameters": ["A",0], "indent": 1},
                    {"code": 412, "parameters": [], "indent": 0},
                    {"code": 111, "parameters": [1,10,0,2,0,0], "indent": 0},
                        {"code": 101, "parameters": ["",0,0,2], "indent": 1},
                        {"code": 401, "parameters": ["La photosynthese, c'est epuisant"], "indent": 1},
                    {"code": 412, "parameters": [], "indent": 0},
                    {"code": 111, "parameters": [1,10,0,3,0,0], "indent": 0},
                        {"code": 101, "parameters": ["",0,0,2], "indent": 1},
                        {"code": 401, "parameters": ["Cette foret... est ma protection."], "indent": 1},
                        {"code": 401, "parameters": ["Enfin, ce carre d'herbe, surtout."], "indent": 1},
                    {"code": 412, "parameters": [], "indent": 0}
                ]
            },
            {
                "conditions": {"switch1Valid": False, "switch2Valid": False, "variableValid": False, "selfSwitchValid": True, "selfSwitchCh": "A"},
                "graphic": {"tileId":9},
                "through": False,
                "list": [

                ]
            }
        ]
    },

    # Event at (x=21, y=5)
    (21, 5): { # Event ID 9
        "id": 9,
        "name": "Protect Cabbit",
        "x": 21, "y": 5,
        "pages": [
            {
                "graphic": {"tileId":55},
                "through": False,
                "list": [
                    {"code": 101, "parameters": ["",0,0,2], "indent": 0},
                    {"code": 401, "parameters": ["Chut ! Ylva nous a vus ?"], "indent": 0},
                    {"code": 401, "parameters": ["Non, attends, elle sent..."], "indent": 0},
                    {"code": 401, "parameters": ["On est foutus, Gerard"], "indent": 0},
                    {"code": 301, "parameters": [0,4,True,True,10], "indent": 0},
                    {"code": 111, "parameters": [1,10,0,1,0,0], "indent": 0},
                        {"code": 101, "parameters": ["",0,0,2], "indent": 1},
                        {"code": 401, "parameters": ["Dis a ma femme... que..."], "indent": 1},
                        {"code": 401, "parameters": ["Je suis parti a la peche"], "indent": 1},
                        {"code": 401, "parameters": ["avec Gerard... pour toujours"], "indent": 1},
                        {"code": 122, "parameters": [9,9,1,0,1], "indent": 1},
                        {"code": 123, "parameters": ["A",0], "indent": 1},
                    {"code": 412, "parameters": [], "indent": 0},
                    {"code": 111, "parameters": [1,10,0,2,0,0], "indent": 0},
                        {"code": 101, "parameters": ["",0,0,2], "indent": 1},
                        {"code": 401, "parameters": ["Bon, on se fait une"], "indent": 1},
                        {"code": 401, "parameters": ["belotte ? "], "indent": 1},
                    {"code": 412, "parameters": [], "indent": 0},
                    {"code": 111, "parameters": [1,10,0,3,0,0], "indent": 0},
                        {"code": 101, "parameters": ["",0,0,2], "indent": 1},
                        {"code": 401, "parameters": ["C'etait pathetique..."], "indent": 1},
                        {"code": 401, "parameters": ["Meme Ylva fait mieux ! "], "indent": 1},
                    {"code": 412, "parameters": [], "indent": 0}
                ]
            },
            {
                "conditions": {"switch1Valid": False, "switch2Valid": False, "variableValid": False, "selfSwitchValid": True, "selfSwitchCh": "A"},
                "graphic": {"tileId":9},
                "through": False,
                "list": [

                ]
            }
        ]
    },

    # Event at (x=22, y=5)
    (22, 5): { # Event ID 10
        "id": 10,
        "name": "Weak Cabbit",
        "x": 22, "y": 5,
        "pages": [
            {
                "graphic": {"tileId":55},
                "through": False,
                "list": [
                    {"code": 101, "parameters": ["",0,0,2], "indent": 0},
                    {"code": 401, "parameters": ["TU AS BUTE MARTIN ! IL ME"], "indent": 0},
                    {"code": 401, "parameters": ["DEVAIT 10 BALLES ! MAINTENANT"], "indent": 0},
                    {"code": 401, "parameters": ["TU VAS PAYER POUR LUI !!"], "indent": 0},
                    {"code": 301, "parameters": [0,4,True,True,10], "indent": 0},
                    {"code": 111, "parameters": [1,10,0,1,0,0], "indent": 0},
                        {"code": 101, "parameters": ["",0,0,2], "indent": 1},
                        {"code": 401, "parameters": ["Au moins... Je pourrais rejoindre"], "indent": 1},
                        {"code": 401, "parameters": ["Martin et lui rapeller qu'il me"], "indent": 1},
                        {"code": 401, "parameters": ["doit toujours 10 balles..."], "indent": 1},
                        {"code": 122, "parameters": [9,9,1,0,1], "indent": 1},
                        {"code": 123, "parameters": ["A",0], "indent": 1},
                    {"code": 412, "parameters": [], "indent": 0},
                    {"code": 111, "parameters": [1,10,0,2,0,0], "indent": 0},
                        {"code": 101, "parameters": ["",0,0,2], "indent": 1},
                        {"code": 401, "parameters": ["REVIENS ICI ! "], "indent": 1},
                        {"code": 401, "parameters": ["JE VEUX MES 10 BALLES !"], "indent": 1},
                    {"code": 412, "parameters": [], "indent": 0},
                    {"code": 111, "parameters": [1,10,0,3,0,0], "indent": 0},
                        {"code": 101, "parameters": ["",0,0,2], "indent": 1},
                        {"code": 401, "parameters": ["Speciale Deci Martin,"], "indent": 1},
                        {"code": 401, "parameters": ["Repose en paix frere !"], "indent": 1},
                    {"code": 412, "parameters": [], "indent": 0}
                ]
            },
            {
                "conditions": {"switch1Valid": False, "switch2Valid": False, "variableValid": False, "selfSwitchValid": True, "selfSwitchCh": "A"},
                "graphic": {"tileId":9},
                "through": False,
                "list": [

                ]
            }
        ]
    },

    # Event at (x=30, y=4)
    (30, 4): { # Event ID 11
        "id": 11,
        "name": "Well Cabbit",
        "x": 30, "y": 4,
        "pages": [
            {
                "graphic": {"tileId":55},
                "through": False,
                "list": [
                    {"code": 101, "parameters": ["",0,0,2], "indent": 0},
                    {"code": 401, "parameters": ["Je ... Je suis un cailloux !"], "indent": 0},
                    {"code": 401, "parameters": ["Une pierre qui parle !"], "indent": 0},
                    {"code": 301, "parameters": [0,4,True,True,10], "indent": 0},
                    {"code": 111, "parameters": [1,10,0,1,0,0], "indent": 0},
                        {"code": 101, "parameters": ["",0,0,2], "indent": 1},
                        {"code": 401, "parameters": ["Adieux mes reves..."], "indent": 1},
                        {"code": 401, "parameters": ["Pierre qui roule-"], "indent": 1},
                        {"code": 122, "parameters": [9,9,1,0,1], "indent": 1},
                        {"code": 123, "parameters": ["A",0], "indent": 1},
                    {"code": 412, "parameters": [], "indent": 0},
                    {"code": 111, "parameters": [1,10,0,2,0,0], "indent": 0},
                        {"code": 101, "parameters": ["",0,0,2], "indent": 1},
                        {"code": 401, "parameters": ["Pierre-Cactus- Puits !"], "indent": 1},
                        {"code": 401, "parameters": ["J'ai gagne !"], "indent": 1},
                    {"code": 412, "parameters": [], "indent": 0},
                    {"code": 111, "parameters": [1,10,0,3,0,0], "indent": 0},
                        {"code": 101, "parameters": ["",0,0,2], "indent": 1},
                        {"code": 401, "parameters": ["La prochaine fois, ne tues "], "indent": 1},
                        {"code": 401, "parameters": ["pas un cactus pour rien..."], "indent": 1},
                    {"code": 412, "parameters": [], "indent": 0}
                ]
            },
            {
                "conditions": {"switch1Valid": False, "switch2Valid": False, "variableValid": False, "selfSwitchValid": True, "selfSwitchCh": "A"},
                "graphic": {"tileId":9},
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
        "name": "Cactus",
        "x": 29, "y": 3,
        "pages": [
            {
                "graphic": {"tileId":26},
                "through": False,
                "list": [
                    {"code": 101, "parameters": ["",0,0,2], "indent": 0},
                    {"code": 401, "parameters": ["Juste un Cactus..."], "indent": 0},
                    {"code": 401, "parameters": ["Juste un Cactus..."], "indent": 0},
                    {"code": 401, "parameters": ["Juste un Cactus..."], "indent": 0},
                    {"code": 101, "parameters": ["ylva_happy",0,0,2], "indent": 0},
                    {"code": 401, "parameters": ["Regarde ! Derriere ! Un lapin !"], "indent": 0},
                    {"code": 101, "parameters": ["",0,0,2], "indent": 0},
                    {"code": 401, "parameters": ["..."], "indent": 0},
                    {"code": 401, "parameters": ["Non je suis un cactus !"], "indent": 0},
                    {"code": 101, "parameters": ["ylva_shocked",0,0,2], "indent": 0},
                    {"code": 401, "parameters": ["Un Lapin-Cactus ! "], "indent": 0},
                    {"code": 401, "parameters": ["C'est tres rare ! "], "indent": 0},
                    {"code": 401, "parameters": ["Attrapes le !"], "indent": 0},
                    {"code": 101, "parameters": ["",0,0,2], "indent": 0},
                    {"code": 401, "parameters": ["*CRACK*"], "indent": 0},
                    {"code": 123, "parameters": ["A",0], "indent": 0}
                ]
            },
            {
                "conditions": {"switch1Valid": False, "switch2Valid": False, "variableValid": False, "selfSwitchValid": True, "selfSwitchCh": "A"},
                "graphic": {"tileId":6},
                "through": True,
                "list": [

                ]
            }
        ]
    },

    # Event at (x=10, y=17)
    (10, 17): { # Event ID 15
        "id": 15,
        "name": "Left Cabbit",
        "x": 10, "y": 17,
        "pages": [
            {
                "graphic": {"tileId":55},
                "through": False,
                "list": [
                    {"code": 101, "parameters": ["",0,0,2], "indent": 0},
                    {"code": 401, "parameters": ["ENFIN ! UN TEMOIN !"], "indent": 0},
                    {"code": 401, "parameters": ["Tu es la, tu as vu,"], "indent": 0},
                    {"code": 401, "parameters": ["c'est lui qui a commence !"], "indent": 0},
                    {"code": 301, "parameters": [0,4,True,True,10], "indent": 0},
                    {"code": 111, "parameters": [1,10,0,1,0,0], "indent": 0},
                        {"code": 101, "parameters": ["",0,0,2], "indent": 1},
                        {"code": 401, "parameters": ["Trahison..."], "indent": 1},
                        {"code": 401, "parameters": ["J'aurais du... me mefier..."], "indent": 1},
                        {"code": 401, "parameters": ["des... associes..."], "indent": 1},
                        {"code": 122, "parameters": [9,9,1,0,1], "indent": 1},
                        {"code": 123, "parameters": ["A",0], "indent": 1},
                    {"code": 412, "parameters": [], "indent": 0},
                    {"code": 111, "parameters": [1,10,0,2,0,0], "indent": 0},
                        {"code": 101, "parameters": ["",0,0,2], "indent": 1},
                        {"code": 401, "parameters": ["He ! Reviens !"], "indent": 1},
                        {"code": 401, "parameters": ["On avait un accord verbal !"], "indent": 1},
                    {"code": 412, "parameters": [], "indent": 0},
                    {"code": 111, "parameters": [1,10,0,3,0,0], "indent": 0},
                        {"code": 101, "parameters": ["",0,0,2], "indent": 1},
                        {"code": 401, "parameters": ["La carotte du milieu EST"], "indent": 1},
                        {"code": 401, "parameters": ["la meilleure. La science le dit."], "indent": 1},
                        {"code": 401, "parameters": ["Merci, la science."], "indent": 1},
                    {"code": 412, "parameters": [], "indent": 0}
                ]
            },
            {
                "conditions": {"switch1Valid": False, "switch2Valid": False, "variableValid": False, "selfSwitchValid": True, "selfSwitchCh": "A"},
                "graphic": {"tileId":9},
                "through": False,
                "list": [

                ]
            }
        ]
    },

    # Event at (x=10, y=16)
    (10, 16): { # Event ID 16
        "id": 16,
        "name": "Right Cabbit",
        "x": 10, "y": 16,
        "pages": [
            {
                "graphic": {"tileId":55},
                "through": False,
                "list": [
                    {"code": 101, "parameters": ["",0,0,2], "indent": 0},
                    {"code": 401, "parameters": ["Non mais tu l'entends ?!"], "indent": 0},
                    {"code": 401, "parameters": ["Il dit que le milieu est"], "indent": 0},
                    {"code": 401, "parameters": ["MEILLEUR que le bout !"], "indent": 0},
                    {"code": 301, "parameters": [0,4,True,True,10], "indent": 0},
                    {"code": 111, "parameters": [1,10,0,1,0,0], "indent": 0},
                        {"code": 101, "parameters": ["",0,0,2], "indent": 1},
                        {"code": 401, "parameters": ["Au moins... je meurs..."], "indent": 1},
                        {"code": 401, "parameters": ["en ayant... raison..."], "indent": 1},
                        {"code": 122, "parameters": [9,9,1,0,1], "indent": 1},
                        {"code": 123, "parameters": ["A",0], "indent": 1},
                    {"code": 412, "parameters": [], "indent": 0},
                    {"code": 111, "parameters": [1,10,0,2,0,0], "indent": 0},
                        {"code": 101, "parameters": ["",0,0,2], "indent": 1},
                        {"code": 401, "parameters": ["Tu nous fais perdre notre"], "indent": 1},
                        {"code": 401, "parameters": ["temps !"], "indent": 1},
                    {"code": 412, "parameters": [], "indent": 0},
                    {"code": 111, "parameters": [1,10,0,3,0,0], "indent": 0},
                        {"code": 101, "parameters": ["",0,0,2], "indent": 1},
                        {"code": 401, "parameters": ["Tu vois, j'ai toujours"], "indent": 1},
                        {"code": 401, "parameters": ["raison !"], "indent": 1},
                    {"code": 412, "parameters": [], "indent": 0}
                ]
            },
            {
                "conditions": {"switch1Valid": False, "switch2Valid": False, "variableValid": False, "selfSwitchValid": True, "selfSwitchCh": "A"},
                "graphic": {"tileId":9},
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