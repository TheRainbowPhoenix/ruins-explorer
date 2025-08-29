HEADER = {
    'description': 'Map Data',
    'exports': ["displayName", "tilesetId", "width", "height", "scrollType", "specifyBattleback", "data", "events"],
}

displayName = "Start Map"
tilesetId = "jrpg" # Corresponds to the key in AssetManager
width = 16
height = 24
scrollType = 0
specifyBattleback = False
HEADER = {
    'description': 'Map Data',
    'exports': ["displayName", "tilesetId", "width", "height", "scrollType", "specifyBattleback", "data", "events"],
}

data = [
    3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3,
    3, 3, 3, 3, 3, 1, 1, 1, 1, 1, 1, 3, 3, 3, 3, 3,
    3, 3, 3, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 3, 3, 3,
    3, 3, 1, 1, 7, 1, 2, 2, 2, 2, 5, 5, 1, 1, 3, 3,
    3, 3, 1, 1, 1, 2, 2, 2, 2, 2, 2, 5, 1, 1, 3, 3,
    3, 1, 1, 1, 1, 8, 8, 1, 8, 8, 8, 1, 1, 1, 1, 3,
    3, 1, 1, 5, 1, 1, 1, 1, 4, 1, 1, 1, 1, 1, 1, 3,
    3, 1, 5, 5, 1, 2, 1, 2, 1, 1, 2, 1, 3, 1, 1, 3,
    3, 1, 1, 5, 1, 2, 2, 2, 2, 2, 2, 1, 1, 3, 3, 3,
    3, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 1, 1, 1, 3, 3,
    3, 1, 3, 1, 1, 1, 1, 2, 2, 2, 2, 1, 1, 5, 1, 3,
    3, 3, 3, 1, 5, 1, 1, 2, 2, 2, 2, 1, 5, 1, 1, 3,
    3, 3, 1, 1, 1, 1, 1, 1, 2, 2, 1, 5, 5, 1, 1, 3,
    3, 1, 2, 2, 2, 5, 1, 1, 2, 2, 1, 1, 5, 1, 1, 3,
    3, 1, 2, 2, 2, 1, 5, 1, 2, 2, 1, 1, 1, 1, 1, 3,
    3, 1, 1, 2, 2, 1, 1, 1, 2, 2, 1, 1, 1, 1, 1, 3,
    3, 3, 3, 1, 1, 1, 1, 1, 2, 1, 5, 5, 1, 1, 3, 3,
    3, 3, 3, 3, 3, 1, 1, 2, 1, 5, 1, 1, 1, 1, 3, 3,
    3, 3, 3, 3, 3, 1, 1, 2, 1, 1, 1, 1, 1, 3, 3, 3,
    3, 3, 1, 3, 1, 3, 3, 1, 1, 1, 3, 3, 3, 3, 1, 3,
    3, 1, 3, 3, 3, 1, 3, 1, 1, 3, 3, 1, 3, 3, 3, 3,
    3, 1, 1, 3, 3, 1, 1, 1, 6, 1, 1, 1, 1, 3, 3, 3,
    3, 3, 3, 3, 3, 3, 3, 8, 6, 3, 3, 3, 3, 3, 3, 3,
    3, 3, 3, 3, 3, 3, 3, 3, 8, 3, 3, 3, 3, 3, 3, 3
]

events: dict = {
    # Event at (x=8, y=23)
    (8, 23): { # Event ID 1
        "id": 1,
        "name": "Ylva",
        "x": 8, "y": 23,
        "pages": [{ # Default / welcome user
            "graphic":{"tileId":97},
            "list":[
                {"code": 101, "parameters": ["ylva_ok", 0, 0, 2]},
                {"code": 401, "parameters": ["Enfin! Mon renfort est arrive."]},
                {"code": 401, "parameters": ["Enleve les mauvaises herbes avant"]},
                {"code": 401, "parameters": ["le coucher du soleil,"]},
                {"code": 401, "parameters": ["Et fais-le bien."]},
                
                {"code": 101, "parameters": []}, 
                {"code": 401, "parameters": ["Sinon ?..."]},

                {"code": 101, "parameters": ["ylva_shocked", 0, 0, 2]},
                {"code": 401, "parameters": ["Si tu ne fais pas pousser"]},
                {"code": 401, "parameters": ["le diner..."]},
                
                {"code": 101, "parameters": []}, 
                {"code": 401, "parameters": ["... ?"]},

                {"code": 101, "parameters": ["ylva_happy", 0, 0, 2]},
                {"code": 401, "parameters": ["...tu le deviendras !"]},
                {"code": 401, "parameters": ["Allez, hop !"]},
                {"code": 401, "parameters": ["Coupe cette herbe !"]},

                {"code": 101, "parameters": []}, 
                {"code": 401, "parameters": ["*Ylva bloque la sortie,"]},
                {"code": 401, "parameters": ["affutant ses ongles*"]},

                {"code": 101, "parameters": []}, 
                {"code": 401, "parameters": ["Objectif :"]},
                {"code": 401, "parameters": ["Couper 10 touffes d'herbe"]},

            ]
        }, { # PAGE 2: Tilled Soil - todo: variableValue=10 
            "conditions": {"variableId": 5, "variableValue": 1, "variableValid": True},
            "graphic": {"tileId": 97},
            "list": [
                {"code": 101, "parameters": ["ylva_ok", 0, 0, 2]},
                {"code": 401, "parameters": ["Bien. Ces herbes ne sont pas"]},
                {"code": 401, "parameters": ["commestibles... Mais le fruit"]},
                {"code": 401, "parameters": ["de tes efforts le sera."]},
                
                {"code": 101, "parameters": []}, 
                {"code": 401, "parameters": ["... ?"]},

                {"code": 101, "parameters": ["ylva_angry", 0, 0, 2]},
                {"code": 401, "parameters": ["Prends cette binette,"]},
                {"code": 401, "parameters": ["va Retourner la terre !"]},
                
                {"code": 101, "parameters": []}, 
                {"code": 401, "parameters": ["C'est tout ?"]},

                {"code": 101, "parameters": ["ylva_ok", 0, 0, 2]},
                {"code": 401, "parameters": ["C'est tout. Pour l'instant."]},
                {"code": 401, "parameters": ["Et ne pense même pas à t'enfuir"]},
                {"code": 401, "parameters": ["Je cours plus vite que toi..."]},

                {"code": 101, "parameters": []}, 
                {"code": 401, "parameters": ["*Ylva bloque toujours le chemin,"]},
                {"code": 401, "parameters": ["assise, feignant de bailler.*"]},

                {"code": 101, "parameters": []}, 
                {"code": 401, "parameters": ["Objectif :"]},
                {"code": 401, "parameters": ["Labourer 5 parcelles de terre"]},
                

            ]

        },{ # PAGE 3: Field plowed - todo: variableValue=5 
            "conditions": {"variableId": 6, "variableValue": 1, "variableValid": True},
            "graphic": {"tileId": 97},
            "list": [
                {"code": 101, "parameters": ["ylva_ok", 0, 0, 2]},
                {"code": 401, "parameters": ["Enfin ! On approche du moment"]},
                {"code": 401, "parameters": [" palpitant. Prends ces graines et"]},
                {"code": 401, "parameters": ["plante-les."]},
                {"code": 401, "parameters": ["Avec grace, cette fois."]},

                {"code": 101, "parameters": ["ylva_happy", 0, 0, 2]},
                {"code": 401, "parameters": ["...Meme si tu n'en as pas."]},
                
                {"code": 101, "parameters": []}, 
                {"code": 401, "parameters": ["... !"]},

                {"code": 101, "parameters": []}, 
                {"code": 401, "parameters": ["*Ylva est toujours la,"]},
                {"code": 401, "parameters": ["croquant une pomme bruyamment"]},
                {"code": 401, "parameters": ["en te regardant travailler.*"]},

                {"code": 101, "parameters": []}, 
                {"code": 401, "parameters": ["Objectif :"]},
                {"code": 401, "parameters": ["Planter 5 graines"]},
            ]

        },{ # PAGE 4: Planted seeds - todo: variableValue=5 
            "conditions": {"variableId": 7, "variableValue": 1, "variableValid": True},
            "graphic": {"tileId": 97},
            "list": [

                {"code": 101, "parameters": []}, 
                {"code": 401, "parameters": ["*Ylva s'etire comme un chat*"]},

                {"code": 101, "parameters": ["ylva_ok", 0, 0, 2]},
                {"code": 401, "parameters": ["Voila. Tu as reussi a ne pas"]},
                {"code": 401, "parameters": ["etre completement inutile..."]},

                {"code": 101, "parameters": []}, 
                {"code": 401, "parameters": ["... ?!"]},

                {"code": 101, "parameters": ["ylva_ok", 0, 0, 2]},
                {"code": 401, "parameters": ["Tu as gagne ... Le droit..."]},
                {"code": 401, "parameters": ["D'aller recolter- Allez, zou!"]},

                {"code": 101, "parameters": []}, 
                {"code": 401, "parameters": ["Cette louve..."]},

                {"code": 101, "parameters": []}, 
                {"code": 401, "parameters": ["Objectif :"]},
                {"code": 401, "parameters": ["Recolter 5 plantations"]},
            ]
        },{ # PAGE 5: Harvest - todo: variableValue=5 
            "conditions": {"variableId": 8, "variableValue": 1, "variableValid": True},
            "graphic": {"tileId": 97},
            "list": [

                {"code": 101, "parameters": []}, 
                {"code": 401, "parameters": ["*Ylva s'agite en souriant*"]},

                {"code": 101, "parameters": ["ylva_ok", 0, 0, 2]},
                {"code": 401, "parameters": ["Tu as gagne ton repas du soir"]},
                {"code": 401, "parameters": ["et le droit de m'accompagner..."]},

                {"code": 101, "parameters": []}, 
                {"code": 401, "parameters": ["Enfin de l'action ?"]},

                {"code": 101, "parameters": ["ylva_happy", 0, 0, 2]},
                {"code": 401, "parameters": ["La chasse. Notre prochain repas"]},
                {"code": 401, "parameters": ["s'appelle 'Lapin'."]},
                {"code": 401, "parameters": ["Ne me decois pas."]},

                {"code": 101, "parameters": []}, 
                {"code": 401, "parameters": ["Objectif :"]},
                {"code": 401, "parameters": ["Suivre Ylva dans la foret"]},
                {"code": 401, "parameters": ["pour chasser le lapin"]},
                {"code": 123, "parameters": ["B",0]} # Turn Self Switch 'B' ON
            ]
        },{
            "conditions": {"selfSwitchCh": "B", "selfSwitchValid": True},
            "graphic": {"tileId": 101},
            "list": [
                {"code": 101, "parameters": ["ylva_ok", 0, 0, 2]},
                {"code": 401, "parameters": ["On y vas ?"]},
                {"code": 401, "parameters": ["Ou tu preferes rester"]},
                {"code": 401, "parameters": ["plante ici ? Hihi-"]},
                # Transfer player to Map 4 at coordinates (7, 22)
                {"code": 201, "parameters": [0, 4, 7, 22]}
            ]
        }
        ]
    },
    (5,4): {
        "id": 1,
        "name": "TEST",
        "x": 8, "y": 23,
        "pages": [{ # Default / welcome user
            "graphic":{"tileId":97},
            "list":[
                {"code": 201, "parameters": [0, 4, 7, 22]}
            ]
        }
        ]
    }
}

for i, (x, y) in enumerate([(7, 18), (7, 17), (4,15), (3,15), (4,14), (4,13), (3,13)]):
    evt_id = i + 2
    events[(x, y)] = { # Event ID 2
        "id": evt_id,
        "name": "Grass1",
        "x": x, "y": y,
        "pages": [
            { # Cut grass
                "graphic": {"tileId": 2},
                "through": True,
                "list": [
                    {"code": 122, "parameters": [5,5,1,0,1]}, # GVL_5 +=1
                    {"code": 101, "parameters": []},
                    {"code": 401, "parameters": ["Vous avez coupe l'herbe"]},
                    {"code": 123, "parameters": ["A", 0]} # Turn Self Switch 'A' ON
                ]
            },
            # Plow the field
            { # (Condition: Self Switch 'A' is ON)
                "conditions": {"selfSwitchCh": "A", "selfSwitchValid": True},
                "graphic": { "tileId": 6 },
                "through": True,
                "list": [
                    {"code": 122, "parameters": [6,6,1,0,1]}, # GVL_6 +=1
                    {"code": 101, "parameters": []},
                    {"code": 401, "parameters": ["La terre est retournee"]},
                    {"code": 123, "parameters": ["B",0]} # Turn Self Switch 'B' ON
                ]
            },
            # Plant seed
            {
                "conditions": {"selfSwitchCh": "B", "selfSwitchValid": True},
                "graphic": {"tileId": 6},
                "through": True,
                "list": [
                    {"code": 101, "parameters": []},
                    {"code": 401, "parameters": ["Que faire avec cette terre ?"]},
                    {"code": 102, "parameters": [["Patate", "Mais", "Ble", "Rien"], 3, 10]}, # Show Choices, store result in Var 10
                
                    {"code": 402, "indent": 0, "parameters": [0]}, # When [Patate]
                        {"code": 101, "indent": 1}, {"code": 401, "indent": 1, "parameters": ["Patate."]},
                        {"code": 356, "indent": 1, "parameters": [f"start_growth({evt_id}, 'potato', 20)"]},
                        {"code": 122, "indent": 1, "parameters": [7,7,1,0,1]}, # GVL_7 +=1
                        {"code": 123, "indent": 1, "parameters": ["C",0]}, # Turn Self Switch 'C' ON                
                    {"code": 412, "indent": 0},
                    
                    {"code": 402, "indent": 0, "parameters": [1]}, # When [Mais]
                        {"code": 101, "indent": 1}, {"code": 401, "indent": 1, "parameters": ["Mais."]},
                        {"code": 356, "indent": 1, "parameters": [f"start_growth({evt_id}, 'mais', 35)"]},
                        {"code": 122, "indent": 1, "parameters": [7,7,1,0,1]}, # GVL_7 +=1
                        {"code": 123, "indent": 1, "parameters": ["C",0]}, # Turn Self Switch 'C' ON
                    {"code": 412, "indent": 0}, # End When

                    {"code": 402, "indent": 0, "parameters": [2]}, # When [Ble]
                        {"code": 101, "indent": 1}, {"code": 401, "indent": 1, "parameters": ["Ble."]},
                        {"code": 356, "indent": 1, "parameters": [f"start_growth({evt_id}, 'ble', 55)"]},
                        {"code": 122, "indent": 1, "parameters": [7,7,1,0,1]}, # GVL_7 +=1
                        {"code": 123, "indent": 1, "parameters": ["C",0]}, # Turn Self Switch 'C' ON
                    {"code": 412, "indent": 0}, # End When

                    {"code": 402, "indent": 0, "parameters": [3]}, # When [**]
                        {"code": 101, "indent": 1}, {"code": 401, "indent": 1, "parameters": ["Ne rien faire..."]},
                        # {"code": 356, "indent": 1, "parameters": ["start_growth(4, 'corn', 45)"]},
                    {"code": 412, "indent": 0}, # End When
                ]
            },
            # Wait for harvest
            {
                "conditions": {"selfSwitchCh": "C", "selfSwitchValid": True},
                "graphic": {"tileId": 100},
                "through": True,
                "list": [
                    # {"code": 101, "parameters": []},
                    # {"code": 401, "parameters": ["Silence ! Ca pousse..."]},
                    {"code": 356, "parameters": [f"check_field({evt_id})"]}
                ]
            },
            # Harvestable
            {
                "conditions": {"selfSwitchCh": "D", "selfSwitchValid": True},
                "graphic": {"tileId": 96},
                "through": True,
                "list": [
                    {"code": 101, "parameters": []},
                    {"code": 401, "parameters": ["Pret a la recolte !"]},
                    {"code": 102, "parameters": [["Recolter", "Attendre"], 1, 10]}, # Show Choices, store result in Var 10
                
                    {"code": 402, "indent": 0, "parameters": [0]}, # When [Recolter]
                        {"code": 101, "indent": 1}, {"code": 401, "indent": 1, "parameters": ["La recolte est bonne !"]},
                        {"code": 356, "indent": 1, "parameters": [f"check_field({evt_id})"]},
                        {"code": 122, "indent": 1, "parameters": [8,8,1,0,1]}, # GVL_8 +=1
                    {"code": 412, "indent": 0},
                    
                    {"code": 402, "indent": 0, "parameters": [1]}, # When [Attendre]
                        {"code": 101, "indent": 1}, {"code": 401, "indent": 1, "parameters": ["La recolte attends."]},
                    {"code": 412, "indent": 0}, # End When
                ]
            }
        ]
    }