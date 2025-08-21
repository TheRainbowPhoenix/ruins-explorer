# The HEADER is crucial for the DataManager to know what's available
# without loading the entire file.
# cpgame/game_data/items.py

HEADER = {
    'exports': ['ITEM_1', 'ITEM_2', 'ITEM_3', 'ITEM_4', 'ITEM_5', 'ITEM_6']
}

ITEM_1 = {"id": 1, "name": "Wood", "price": 5, "description": "A sturdy log from the forest."}
ITEM_2 = {"id": 2, "name": "Stone", "price": 2, "description": "A common piece of rock."}
ITEM_3 = {"id": 3, "name": "Herb", "price": 10, "description": "A medicinal herb."}
ITEM_4 = {"id": 4, "name": "Potato", "price": 50, "description": "A freshly harvested potato."}
ITEM_5 = {"id": 5, "name": "Potato Seed", "price": 10, "description": "Plant this to grow potatoes."}
ITEM_6 = {"id": 6, "name": "Corn Seed", "price": 20, "description": "Plant this to grow corn."}