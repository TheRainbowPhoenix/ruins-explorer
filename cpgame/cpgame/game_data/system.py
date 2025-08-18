# The HEADER is crucial for the DataManager to know what's available
# without loading the entire file.
HEADER = {
    'description': 'Contains system config',
    'exports': ["party_members", "test_battlers"], # TODO: add some
}

party_members = ["ACTOR_1"]

test_battlers = [{
        "actor_id": 1,
        "equips": [1,0,0,0,0],
        "level": 1
    }]
