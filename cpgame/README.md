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

## Performance notes

"empty" uses 736B + 294_624 free

import gint  (+gc)= 768B so "import gint" = 32B 
import * from gint = 2528B !!!

before imports : 2752 B
before splash: 4288 B
after splash: 4384 B
Splash ~1728B

profiler class uses 1376 B (!) 


Assets Manager @ Templar = 3616B
Assets Manager @ JRPG = 224B

Scene_MenuScene = 480B


(old :)
main menu uses 229_440 (of 295360)
templar uses 230_690

### General infos about memory usage
empty class = 128 B
10x inst of class = 256B
10x lambda = 256B
10x functions = 320B

strings = bytes in size. 'abc' x10 = 96
10x 2 items tuple = 96B
10x empty list = 416B (!)
10x dict = 256B



### Rect tests
(100x)
MinimalRect class + __slots__ = 5344 B
namedtuple  3744 B
tuple       3184 B
Dict        5360 B



## Gameplay notes

Livestock:
- Chicken (price 10)
- Pigs
- Turkeys
- Cows
- ??

Road building:
- Build roads (price 10, +1/m)
- Fertilize soil (price 10, +1/m)

Plants:
- Potato (price 10)
- Lettuce (price x)
- Strawberries
- wheat
- corn
- grapes
- apples tree
- orange tree
- ?? +

Extra:
- Humidifier
- bird house
- scarecrow
- pond
- 

Distribution:
- ??
- Small market (cost 400, +?/m)
- Store front (cost ??, +?/m)
- ??

First you need to build a Fertilize soil (you can undo this but you loose money)
Then you plant
