# The HEADER is crucial for the DataManager to know what's available
# without loading the entire file.
HEADER = {
    'description': 'Contains system config',
    'exports': ["party_members", "test_battlers", "start_map_id", "start_x", "start_y"], # TODO: add some
}

party_members = [1]

test_battlers = [{
        "actor_id": 2,
        "equips": [1,0,0,0,0],
        "level": 1
    }]

start_map_id = 3
start_x = 8
start_y = 22