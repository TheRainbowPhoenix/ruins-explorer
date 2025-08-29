
try:
    from typing import Dict, List, Optional, Any, Tuple
except:
    pass

import math

from cpgame.systems.jrpg import JRPG
from cpgame.engine.assets import Tilemap
from cpgame.game_objects.event import GameEvent
from cpgame.game_objects.interpreter import GameInterpreter

# TODO: move it elsewhere
class GameEvent_Simple:
    """A simple data container for a map event."""
    def __init__(self, event_data: Dict):
        # TODO: this would parse pages and conditions.
        # For now, we take the first page directly.
        page = event_data.get('pages', [{}])[0]
        graphic = page.get('graphic', {})
        self.tile_id = graphic.get('tile_id', 0)
        self.payload = page.get('payload', None)

class GameMap:
    """Manages map data, scrolling, and passage determination."""
    def __init__(self):
        self._map_id = 0
        self._map_proxy = None
        self._data = None
        self.events: Dict[Tuple[int, int], GameEvent] = {}
        # Cache loaded props
        self._properties: Dict[str, Any] = {}
        self.interpreter = GameInterpreter()
        
        # TODO: add more 
        self.need_refresh: bool = False
        self._dirty_tiles = set()

    def setup(self, map_id: int):
        """Loads and initializes a new map."""
        # print("Setting up map ID:", map_id)
        self._map_id = map_id
        
        if JRPG.data and JRPG.data.maps:
            self._map_proxy = JRPG.data.maps[map_id]

            self.events.clear()
            self._properties.clear() # Clear cached properties
            self.interpreter.clear()

            with self._map_proxy.load("events") as event_data:
                if event_data:
                    for pos, data in event_data.items():
                        if not isinstance(pos, tuple):
                            if pos == "__name__":
                                continue

                            print("ERR: invalid pos (x, y) tuple")

                        # The key is a string from the file, convert to tuple
                        # pos_tuple = tuple(map(int, pos.strip('()').split(',')))
                        self.events[pos] = GameEvent(map_id, data)
    
    def _get_property(self, prop_name: str, default: Any = None) -> Any:
        """Lazy-loads a property from the map data file."""
        if prop_name in self._properties:
            return self._properties[prop_name]
        
        if self._map_proxy:
            with self._map_proxy.load(prop_name) as value:
                self._properties[prop_name] = value
                return value
        return default

    @property
    def width(self) -> int:
        return self._get_property('width', 0)

    @property
    def height(self) -> int:
        return self._get_property('height', 0)
    
    @property
    def tileset_id(self) -> str:
        return self._get_property('tilesetId', 'jrpg')
    
    def update(self):
        """Update the map's interpreter and all its events."""
        if self.need_refresh:
            self.refresh_events()
        
        if self.interpreter.is_running():
            self.interpreter.update()
        
        for event in self.events.values():
            event.update()

    def refresh_events(self):
        """Force all events to re-evaluate their pages."""
        for event in self.events.values():
            event.refresh()
        self.need_refresh = False
    
    def start_event_interpreter(self, event: GameEvent):
        """Starts the interpreter if it's not already busy."""
        if not self.interpreter.is_running():
            self.interpreter.setup(event.command_list, event.id)

    def tile_id(self, x: int, y: int) -> int:
        map_data = self._get_property('data')
        if map_data and 0 <= x < self.width and 0 <= y < self.height:
            return map_data[y * self.width + x]
        return 0

    def set_tile_dirty(self, x, y):
        """Flags a specific tile to be redrawn by the scene."""
        self._dirty_tiles.add((x, y))

    def get_dirty_tiles(self) -> set:
        """Returns the set of dirty tiles and then clears it."""
        tiles = self._dirty_tiles.copy()
        self._dirty_tiles.clear()
        return tiles

    def is_passable(self, x: int, y: int, tileset: 'Tilemap') -> bool:
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        
        if (x, y) in self.events:
            ev = self.events[(x, y)]
            if ev and not ev.through:
                return False
        
        tile = self.tile_id(x, y)
        return tile not in tileset.solid
    
    def encounter_list(self) -> List[Dict]:
        """Gets the encounter list for the current map."""
        return self._get_property('encounterList', [])

    def region_id(self, x: int, y: int) -> int:
        """Gets the region ID for a specific coordinate."""
        # This assumes region data is stored in the 4th layer of the map data array
        data = self._get_property('data')
        # TODO: 
        # if data and 0 <= x < self.width and 0 <= y < self.height:
        #     # RPG Maker stores region ID in the upper 8 bits of the 4th layer tile
        #     return (data[y * self.width + x + (self.width * self.height * 3)] >> 8) & 0xFF
        return 0

class GameMapFULL_TODO:
    """
    This class handles maps. It includes scrolling and passage determination
    functions. The instance of this class is referenced by $game_map.
    """
    @property
    def screen(self) -> Any:
        return self._screen
    
    @property
    def interpreter(self) -> Any:
        return self._interpreter
    
    @property
    def events(self) -> Dict[int, Any]:
        return self._events
    
    @property
    def display_x(self) -> float:
        return self._display_x
    
    @property
    def display_y(self) -> float:
        return self._display_y
    
    # @property
    # def parallax_name(self) -> str:
    #     return self._parallax_name
    
    # @property
    # def vehicles(self) -> List[Any]:
    #     return self._vehicles
    
    # @property
    # def battleback1_name(self) -> Optional[str]:
    #     return self._battleback1_name
    
    # @property
    # def battleback2_name(self) -> Optional[str]:
    #     return self._battleback2_name
    
    @property
    def name_display(self) -> bool:
        return self._name_display
    
    @name_display.setter
    def name_display(self, value: bool) -> None:
        self._name_display = value
    
    @property
    def need_refresh(self) -> bool:
        return self._need_refresh
    
    @need_refresh.setter
    def need_refresh(self, value: bool) -> None:
        self._need_refresh = value
    
    #--------------------------------------------------------------------------
    # * Object Initialization
    #--------------------------------------------------------------------------
    def __init__(self):
        self._screen = None # GameScreen()
        self._interpreter = None # GameInterpreter()
        self._map_id = 0
        self._events = {}
        self._display_x = 0.0
        self._display_y = 0.0
        # self.create_vehicles()
        self._name_display = True
        self._need_refresh = False