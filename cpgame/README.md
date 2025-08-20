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

Prio: test shop, see what needs to be done (mabe add GameItem class ? Check why shop is empty)
Make the command to open scenes (Battle, mini-games) generic for re-use
Add the menu with actors list
Add drawng methods to draw actor faces from dialogs

1. Finish the GameMap, make it load map from files -- OKish, tiles have to be dynamic
2. Roll out various Game* classes -- In progress
3. Modules Vocab (for text templates) + SceneManager + BattleManager
4. Windows support (basic, polyfill) -- In progress
5. Scenes Battle + Scene Map
6. Add UI windows (like RPG Maker) and test the data
7. All Scenes ported
8. Add save / load support
9. Finish Windows support
10. Plugins support -- In progress
11. Settings menu + rebind keys
12. Landing screens with how-to guide (explain numpad moves) 

How to save binary files ? does repr works ? 
Make an on-device fxconv to serialize and deserialize on the fly

