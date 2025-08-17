# cpGame

## Structure

```
├── main.py                 # The simple, single entry point to run the game.
│
├── game_assets/            # Add your own assets here (in python)
│   ├── __init__.py
│   ├── jrpg_data.py        # Data for the JRPG: map layout, objects, etc.
│   └── templar_data.py     # All data from the original templar_data as an example
│
├── engine/
│   ├── __init__.py
│   ├── animation.py        # Animation classes.
│   ├── assets.py           # The new Asset Manager.
│   ├── game.py             # The main Game class with the fixed-timestep loop.
│   ├── geometry.py         # The vec2 and rect classes.
│   ├── scene.py            # The base Scene class.
│   └── systems.py          # InputManager and Camera classes.
│
└── game_scenes/            # Add your own scenes here (in python)
    ├── __init__.py
    ├── jrpg_scene.py       # The JRPG top-down game scene.
    ├── menu_scene.py       # A new title screen to choose a game.
    └── templar_scene.py    # The Templar side-scrolling game scene.
```

## TODO

How to save binary files ? does repr works ? 
Make an on-device fxconv to serialize and deserialize on the fly

