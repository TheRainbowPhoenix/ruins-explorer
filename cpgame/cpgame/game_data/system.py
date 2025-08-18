# The HEADER is crucial for the DataManager to know what's available
# without loading the entire file.
HEADER = {
    'description': 'Contains system config',
    'exports': ["party_members", "test_battlers", "start_map_id"], # TODO: add some
}

party_members = ["ACTOR_1"]

test_battlers = [{
        "actor_id": 1,
        "equips": [1,0,0,0,0],
        "level": 1
    }]

start_map_id = 1
