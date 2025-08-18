
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
        if self.interpreter.is_running():
            self.interpreter.update()
        
        for event in self.events.values():
            event.update()
    
    def start_event_interpreter(self, event: GameEvent):
        """Starts the interpreter if it's not already busy."""
        if not self.interpreter.is_running():
            self.interpreter.setup(event.command_list, event.id)

    def tile_id(self, x: int, y: int) -> int:
        map_data = self._get_property('data')
        if map_data and 0 <= x < self.width and 0 <= y < self.height:
            return map_data[y * self.width + x]
        return 0

    def is_passable(self, x: int, y: int, tileset: 'Tilemap') -> bool:
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        if (x, y) in self.events:
            return False
        tile = self.tile_id(x, y)
        return tile not in tileset.solid

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
    
if False:
    #--------------------------------------------------------------------------
    # * Setup
    #--------------------------------------------------------------------------
    def setup(self, map_id: int) -> None:
        self._map_id = map_id
        self._map = None # TODO: load_data(sprintf("Data/Map%03d.rvdata2", self._map_id))
        self._tileset_id = self._map.tileset_id
        self._display_x = 0.0
        self._display_y = 0.0
        self.referesh_vehicles()
        self.setup_events()
        self.setup_scroll()
        self.setup_parallax()
        self.setup_battleback()
        self._need_refresh = False
    
    #--------------------------------------------------------------------------
    # * Create Vehicles
    #--------------------------------------------------------------------------
    def create_vehicles(self) -> None:
        self._vehicles = []
        # self._vehicles.append(GameVehicle("boat"))
        # self._vehicles.append(GameVehicle("ship"))
        # self._vehicles.append(GameVehicle("airship"))
    
    #--------------------------------------------------------------------------
    # * Refresh Vehicles
    #--------------------------------------------------------------------------
    def referesh_vehicles(self) -> None:
        for vehicle in self._vehicles:
            vehicle.refresh()
    
    #--------------------------------------------------------------------------
    # * Get Vehicle
    #--------------------------------------------------------------------------
    def vehicle(self, type_str: str) -> Optional[Any]:
        if type_str == "boat":
            return self._vehicles[0]
        elif type_str == "ship":
            return self._vehicles[1]
        elif type_str == "airship":
            return self._vehicles[2]
        else:
            return None
    
    #--------------------------------------------------------------------------
    # * Get Boat
    #--------------------------------------------------------------------------
    def boat(self) -> Any:
        return self._vehicles[0]
    
    #--------------------------------------------------------------------------
    # * Get Ship
    #--------------------------------------------------------------------------
    def ship(self) -> Any:
        return self._vehicles[1]
    
    #--------------------------------------------------------------------------
    # * Get Airship
    #--------------------------------------------------------------------------
    def airship(self) -> Any:
        return self._vehicles[2]
    
    #--------------------------------------------------------------------------
    # * Event Setup
    #--------------------------------------------------------------------------
    def setup_events(self) -> None:
        self._events = {}
        for i, event in self._map.events.items():
            self._events[i] = Game_Event(self._map_id, event)
        self._common_events = [Game_CommonEvent(common_event.id) for common_event in self.parallel_common_events()]
        self.refresh_tile_events()
    
    #--------------------------------------------------------------------------
    # * Get Array of Parallel Common Events
    #--------------------------------------------------------------------------
    def parallel_common_events(self) -> List[Any]:
        return [event for event in JRPG.data.common_events if event and event.parallel()]
    
    #--------------------------------------------------------------------------
    # * Scroll Setup
    #--------------------------------------------------------------------------
    def setup_scroll(self) -> None:
        self._scroll_direction = 2
        self._scroll_rest = 0
        self._scroll_speed = 4
    
    #--------------------------------------------------------------------------
    # * Parallax Background Setup
    #--------------------------------------------------------------------------
    def setup_parallax(self) -> None:
        self._parallax_name = self._map.parallax_name
        self._parallax_loop_x = self._map.parallax_loop_x
        self._parallax_loop_y = self._map.parallax_loop_y
        self._parallax_sx = self._map.parallax_sx
        self._parallax_sy = self._map.parallax_sy
        self._parallax_x = 0
        self._parallax_y = 0
    
    #--------------------------------------------------------------------------
    # * Set Up Battle Background
    #--------------------------------------------------------------------------
    def setup_battleback(self) -> None:
        if self._map.specify_battleback:
            self._battleback1_name = self._map.battleback1_name
            self._battleback2_name = self._map.battleback2_name
        else:
            self._battleback1_name = None
            self._battleback2_name = None
    
    #--------------------------------------------------------------------------
    # * Set Display Position
    #--------------------------------------------------------------------------
    def set_display_pos(self, x: int, y: int) -> None:
        if not self.loop_horizontal():
            x = max(0, min(x, self.width() - self.screen_tile_x()))
        if not self.loop_vertical():
            y = max(0, min(y, self.height() - self.screen_tile_y()))
        self._display_x = (x + self.width()) % self.width()
        self._display_y = (y + self.height()) % self.height()
        self._parallax_x = x
        self._parallax_y = y
    
    #--------------------------------------------------------------------------
    # * Calculate X Coordinate of Parallax Display Origin
    #--------------------------------------------------------------------------
    def parallax_ox(self, bitmap: Any) -> int:
        if self._parallax_loop_x:
            return self._parallax_x * 16
        else:
            w1 = max(bitmap.width - Graphics.width, 0)
            w2 = max(self.width() * 32 - Graphics.width, 1)
            return self._parallax_x * 16 * w1 // w2
    
    #--------------------------------------------------------------------------
    # * Calculate Y Coordinate of Parallax Display Origin
    #--------------------------------------------------------------------------
    def parallax_oy(self, bitmap: Any) -> int:
        if self._parallax_loop_y:
            return self._parallax_y * 16
        else:
            h1 = max(bitmap.height - Graphics.height, 0)
            h2 = max(self.height() * 32 - Graphics.height, 1)
            return self._parallax_y * 16 * h1 // h2
    
    #--------------------------------------------------------------------------
    # * Get Map ID
    #--------------------------------------------------------------------------
    def map_id(self) -> int:
        return self._map_id
    
    #--------------------------------------------------------------------------
    # * Get Tileset
    #--------------------------------------------------------------------------
    def tileset(self) -> Any:
        return JRPG.data.tilesets.get(self._tileset_id)
    
    #--------------------------------------------------------------------------
    # * Get Display Name
    #--------------------------------------------------------------------------
    def display_name(self) -> str:
        return self._map.display_name
    
    #--------------------------------------------------------------------------
    # * Get Width
    #--------------------------------------------------------------------------
    def width(self) -> int:
        return self._map.width
    
    #--------------------------------------------------------------------------
    # * Get Height
    #--------------------------------------------------------------------------
    def height(self) -> int:
        return self._map.height
    
    #--------------------------------------------------------------------------
    # * Loop Horizontally?
    #--------------------------------------------------------------------------
    def loop_horizontal(self) -> bool:
        return self._map.scroll_type == 2 or self._map.scroll_type == 3
    
    #--------------------------------------------------------------------------
    # * Loop Vertically?
    #--------------------------------------------------------------------------
    def loop_vertical(self) -> bool:
        return self._map.scroll_type == 1 or self._map.scroll_type == 3
    
    #--------------------------------------------------------------------------
    # * Get Whether Dash is Disabled
    #--------------------------------------------------------------------------
    def disable_dash(self) -> bool:
        return self._map.disable_dashing
    
    #--------------------------------------------------------------------------
    # * Get Encounter List
    #--------------------------------------------------------------------------
    def encounter_list(self) -> List[Any]:
        return self._map.encounter_list
    
    #--------------------------------------------------------------------------
    # * Get Encounter Steps
    #--------------------------------------------------------------------------
    def encounter_step(self) -> int:
        return self._map.encounter_step
    
    #--------------------------------------------------------------------------
    # * Get Map Data
    #--------------------------------------------------------------------------
    def data(self) -> Any:
        return self._map.data
    
    #--------------------------------------------------------------------------
    # * Determine if Field Type
    #--------------------------------------------------------------------------
    def overworld(self) -> bool:
        return self.tileset().mode == 0
    
    #--------------------------------------------------------------------------
    # * Number of Horizontal Tiles on Screen
    #--------------------------------------------------------------------------
    def screen_tile_x(self) -> int:
        return Graphics.width // 32
    
    #--------------------------------------------------------------------------
    # * Number of Vertical Tiles on Screen
    #--------------------------------------------------------------------------
    def screen_tile_y(self) -> int:
        return Graphics.height // 32
    
    #--------------------------------------------------------------------------
    # * Calculate X Coordinate, Minus Display Coordinate
    #--------------------------------------------------------------------------
    def adjust_x(self, x: int) -> int:
        if self.loop_horizontal() and x < self._display_x - (self.width() - self.screen_tile_x()) / 2:
            return x - self._display_x + self._map.width
        else:
            return x - self._display_x
    
    #--------------------------------------------------------------------------
    # * Calculate Y Coordinate, Minus Display Coordinate
    #--------------------------------------------------------------------------
    def adjust_y(self, y: int) -> int:
        if self.loop_vertical() and y < self._display_y - (self.height() - self.screen_tile_y()) / 2:
            return y - self._display_y + self._map.height
        else:
            return y - self._display_y
    
    #--------------------------------------------------------------------------
    # * Calculate X Coordinate After Loop Adjustment
    #--------------------------------------------------------------------------
    def round_x(self, x: int) -> int:
        return (x + self.width()) % self.width() if self.loop_horizontal() else x
    
    #--------------------------------------------------------------------------
    # * Calculate Y Coordinate After Loop Adjustment
    #--------------------------------------------------------------------------
    def round_y(self, y: int) -> int:
        return (y + self.height()) % self.height() if self.loop_vertical() else y
    
    #--------------------------------------------------------------------------
    # * Calculate X Coordinate Shifted One Tile in Specific Direction
    #   (No Loop Adjustment)
    #--------------------------------------------------------------------------
    def x_with_direction(self, x: int, d: int) -> int:
        return x + (1 if d == 6 else -1 if d == 4 else 0)
    
    #--------------------------------------------------------------------------
    # * Calculate Y Coordinate Shifted One Tile in Specific Direction
    #   (No Loop Adjustment)
    #--------------------------------------------------------------------------
    def y_with_direction(self, y: int, d: int) -> int:
        return y + (1 if d == 2 else -1 if d == 8 else 0)
    
    #--------------------------------------------------------------------------
    # * Calculate X Coordinate Shifted One Tile in Specific Direction
    #   (With Loop Adjustment)
    #--------------------------------------------------------------------------
    def round_x_with_direction(self, x: int, d: int) -> int:
        return self.round_x(x + (1 if d == 6 else -1 if d == 4 else 0))
    
    #--------------------------------------------------------------------------
    # * Calculate Y Coordinate Shifted One Tile in Specific Direction
    #   (With Loop Adjustment)
    #--------------------------------------------------------------------------
    def round_y_with_direction(self, y: int, d: int) -> int:
        return self.round_y(y + (1 if d == 2 else -1 if d == 8 else 0))
    
    #--------------------------------------------------------------------------
    # * Automatically Switch BGM and BGS
    #--------------------------------------------------------------------------
    def autoplay(self) -> None:
        if self._map.autoplay_bgm:
            self._map.bgm.play()
        if self._map.autoplay_bgs:
            self._map.bgs.play()
    
    #--------------------------------------------------------------------------
    # * Refresh
    #--------------------------------------------------------------------------
    def refresh(self) -> None:
        for event in self._events.values():
            event.refresh()
        for event in self._common_events:
            event.refresh()
        self.refresh_tile_events()
        self._need_refresh = False
    
    #--------------------------------------------------------------------------
    # * Refresh Array of Tile-Handling Events
    #--------------------------------------------------------------------------
    def refresh_tile_events(self) -> None:
        self._tile_events = [event for event in self._events.values() if event.tile()]
    
    #--------------------------------------------------------------------------
    # * Get Array of Events at Designated Coordinates
    #--------------------------------------------------------------------------
    def events_xy(self, x: int, y: int) -> List[Any]:
        return [event for event in self._events.values() if event.pos(x, y)]
    
    #--------------------------------------------------------------------------
    # * Get Array of Events at Designated Coordinates (Except Pass-Through)
    #--------------------------------------------------------------------------
    def events_xy_nt(self, x: int, y: int) -> List[Any]:
        return [event for event in self._events.values() if event.pos_nt(x, y)]
    
    #--------------------------------------------------------------------------
    # * Get Array of Tile-Handling Events at Designated Coordinates
    #   (Except Pass-Through)
    #--------------------------------------------------------------------------
    def tile_events_xy(self, x: int, y: int) -> List[Any]:
        return [event for event in self._tile_events if event.pos_nt(x, y)]
    
    #--------------------------------------------------------------------------
    # * Get ID of Events at Designated Coordinates (One Only)
    #--------------------------------------------------------------------------
    def event_id_xy(self, x: int, y: int) -> int:
        list_events = self.events_xy(x, y)
        return 0 if not list_events else list_events[0].id
    
    #--------------------------------------------------------------------------
    # * Scroll Down
    #--------------------------------------------------------------------------
    def scroll_down(self, distance: float) -> None:
        if self.loop_vertical():
            self._display_y += distance
            self._display_y %= self._map.height
            if self._parallax_loop_y:
                self._parallax_y += distance
        else:
            last_y = self._display_y
            self._display_y = min(self._display_y + distance, self.height() - self.screen_tile_y())
            self._parallax_y += self._display_y - last_y
    
    #--------------------------------------------------------------------------
    # * Scroll Left
    #--------------------------------------------------------------------------
    def scroll_left(self, distance: float) -> None:
        if self.loop_horizontal():
            self._display_x += self._map.width - distance
            self._display_x %= self._map.width
            if self._parallax_loop_x:
                self._parallax_x -= distance
        else:
            last_x = self._display_x
            self._display_x = max(self._display_x - distance, 0)
            self._parallax_x += self._display_x - last_x
    
    #--------------------------------------------------------------------------
    # * Scroll Right
    #--------------------------------------------------------------------------
    def scroll_right(self, distance: float) -> None:
        if self.loop_horizontal():
            self._display_x += distance
            self._display_x %= self._map.width
            if self._parallax_loop_x:
                self._parallax_x += distance
        else:
            last_x = self._display_x
            self._display_x = min(self._display_x + distance, self.width() - self.screen_tile_x())
            self._parallax_x += self._display_x - last_x
    
    #--------------------------------------------------------------------------
    # * Scroll Up
    #--------------------------------------------------------------------------
    def scroll_up(self, distance: float) -> None:
        if self.loop_vertical():
            self._display_y += self._map.height - distance
            self._display_y %= self._map.height
            if self._parallax_loop_y:
                self._parallax_y -= distance
        else:
            last_y = self._display_y
            self._display_y = max(self._display_y - distance, 0)
            self._parallax_y += self._display_y - last_y
    
    #--------------------------------------------------------------------------
    # * Determine Valid Coordinates
    #--------------------------------------------------------------------------
    def valid(self, x: int, y: int) -> bool:
        return 0 <= x < self.width() and 0 <= y < self.height()
    
    #--------------------------------------------------------------------------
    # * Check Passage
    #     bit:  Inhibit passage check bit
    #--------------------------------------------------------------------------
    def check_passage(self, x: int, y: int, bit: int) -> bool:
        for tile_id in self.all_tiles(x, y):
            flag = self.tileset().flags[tile_id]
            if flag & 0x10 != 0:  # [☆]: No effect on passage
                continue
            if flag & bit == 0:   # [○] : Passable
                return True
            if flag & bit == bit: # [×] : Impassable
                return False
        return False  # Impassable
    
    #--------------------------------------------------------------------------
    # * Get Tile ID at Specified Coordinates
    #--------------------------------------------------------------------------
    def tile_id(self, x: int, y: int, z: int) -> int:
        return self._map.data[x, y, z] if self._map.data[x, y, z] else 0
    
    #--------------------------------------------------------------------------
    # * Get Array of All Layer Tiles (Top to Bottom) at Specified Coordinates
    #--------------------------------------------------------------------------
    def layered_tiles(self, x: int, y: int) -> List[int]:
        return [self.tile_id(x, y, z) for z in [2, 1, 0]]
    
    #--------------------------------------------------------------------------
    # * Get Array of All Tiles (Including Events) at Specified Coordinates
    #--------------------------------------------------------------------------
    def all_tiles(self, x: int, y: int) -> List[int]:
        return [ev.tile_id for ev in self.tile_events_xy(x, y)] + self.layered_tiles(x, y)
    
    #--------------------------------------------------------------------------
    # * Get Type of Auto Tile at Specified Coordinates
    #--------------------------------------------------------------------------
    def autotile_type(self, x: int, y: int, z: int) -> int:
        tile_id = self.tile_id(x, y, z)
        return (tile_id - 2048) // 48 if tile_id >= 2048 else -1
    
    #--------------------------------------------------------------------------
    # * Determine Passability of Normal Character
    #     d:  direction (2,4,6,8)
    #    Determines whether the tile at the specified coordinates is passable
    #    in the specified direction.
    #--------------------------------------------------------------------------
    def passable(self, x: int, y: int, d: int) -> bool:
        return self.check_passage(x, y, (1 << (d // 2 - 1)) & 0x0f)
    
    #--------------------------------------------------------------------------
    # * Determine if Passable by Boat
    #--------------------------------------------------------------------------
    def boat_passable(self, x: int, y: int) -> bool:
        return self.check_passage(x, y, 0x0200)
    
    #--------------------------------------------------------------------------
    # * Determine if Passable by Ship
    #--------------------------------------------------------------------------
    def ship_passable(self, x: int, y: int) -> bool:
        return self.check_passage(x, y, 0x0400)
    
    #--------------------------------------------------------------------------
    # * Determine if Airship can Land
    #--------------------------------------------------------------------------
    def airship_land_ok(self, x: int, y: int) -> bool:
        return self.check_passage(x, y, 0x0800) and self.check_passage(x, y, 0x0f)
    
    #--------------------------------------------------------------------------
    # * Determine Flag for All Layers at Specified Coordinates
    #--------------------------------------------------------------------------
    def layered_tiles_flag(self, x: int, y: int, bit: int) -> bool:
        return any(self.tileset().flags[tile_id] & bit != 0 for tile_id in self.layered_tiles(x, y))
    
    #--------------------------------------------------------------------------
    # * Determine if Ladder
    #--------------------------------------------------------------------------
    def ladder(self, x: int, y: int) -> bool:
        return self.valid(x, y) and self.layered_tiles_flag(x, y, 0x20)
    
    #--------------------------------------------------------------------------
    # * Determine if Bush
    #--------------------------------------------------------------------------
    def bush(self, x: int, y: int) -> bool:
        return self.valid(x, y) and self.layered_tiles_flag(x, y, 0x40)
    
    #--------------------------------------------------------------------------
    # * Determine if Counter
    #--------------------------------------------------------------------------
    def counter(self, x: int, y: int) -> bool:
        return self.valid(x, y) and self.layered_tiles_flag(x, y, 0x80)
    
    #--------------------------------------------------------------------------
    # * Determine if Damage Floor
    #--------------------------------------------------------------------------
    def damage_floor(self, x: int, y: int) -> bool:
        return self.valid(x, y) and self.layered_tiles_flag(x, y, 0x100)
    
    #--------------------------------------------------------------------------
    # * Get Terrain Tag
    #--------------------------------------------------------------------------
    def terrain_tag(self, x: int, y: int) -> int:
        if not self.valid(x, y):
            return 0
        for tile_id in self.layered_tiles(x, y):
            tag = self.tileset().flags[tile_id] >> 12
            if tag > 0:
                return tag
        return 0
    
    #--------------------------------------------------------------------------
    # * Get Region ID
    #--------------------------------------------------------------------------
    def region_id(self, x: int, y: int) -> int:
        return self._map.data[x, y, 3] >> 8 if self.valid(x, y) else 0
    
    #--------------------------------------------------------------------------
    # * Start Scroll
    #--------------------------------------------------------------------------
    def start_scroll(self, direction: int, distance: int, speed: int) -> None:
        self._scroll_direction = direction
        self._scroll_rest = distance
        self._scroll_speed = speed
    
    #--------------------------------------------------------------------------
    # * Determine if Scrolling
    #--------------------------------------------------------------------------
    def scrolling(self) -> bool:
        return self._scroll_rest > 0
    
    #--------------------------------------------------------------------------
    # * Frame Update
    #     main:  Interpreter update flag
    #--------------------------------------------------------------------------
    def update(self, main: bool = False) -> None:
        if self._need_refresh:
            self.refresh()
        if main:
            self.update_interpreter()
        self.update_scroll()
        self.update_events()
        self.update_vehicles()
        self.update_parallax()
        self._screen.update()
    
    #--------------------------------------------------------------------------
    # * Update Scroll
    #--------------------------------------------------------------------------
    def update_scroll(self) -> None:
        if not self.scrolling():
            return
        last_x = self._display_x
        last_y = self._display_y
        self.do_scroll(self._scroll_direction, self.scroll_distance())
        if self._display_x == last_x and self._display_y == last_y:
            self._scroll_rest = 0
        else:
            self._scroll_rest -= self.scroll_distance()
    
    #--------------------------------------------------------------------------
    # * Calculate Scroll Distance
    #--------------------------------------------------------------------------
    def scroll_distance(self) -> float:
        return (2 ** self._scroll_speed) / 256.0
    
    #--------------------------------------------------------------------------
    # * Execute Scroll
    #--------------------------------------------------------------------------
    def do_scroll(self, direction: int, distance: float) -> None:
        if direction == 2:
            self.scroll_down(distance)
        elif direction == 4:
            self.scroll_left(distance)
        elif direction == 6:
            self.scroll_right(distance)
        elif direction == 8:
            self.scroll_up(distance)
    
    #--------------------------------------------------------------------------
    # * Update Events
    #--------------------------------------------------------------------------
    def update_events(self) -> None:
        for event in self._events.values():
            event.update()
        for event in self._common_events:
            event.update()
    
    #--------------------------------------------------------------------------
    # * Update Vehicles
    #--------------------------------------------------------------------------
    def update_vehicles(self) -> None:
        for vehicle in self._vehicles:
            vehicle.update()
    
    #--------------------------------------------------------------------------
    # * Update Parallax
    #--------------------------------------------------------------------------
    def update_parallax(self) -> None:
        if self._parallax_loop_x:
            self._parallax_x += self._parallax_sx / 64.0
        if self._parallax_loop_y:
            self._parallax_y += self._parallax_sy / 64.0
    
    #--------------------------------------------------------------------------
    # * Change Tileset
    #--------------------------------------------------------------------------
    def change_tileset(self, tileset_id: int) -> None:
        self._tileset_id = tileset_id
        self.refresh()
    
    #--------------------------------------------------------------------------
    # * Change Battle Background
    #--------------------------------------------------------------------------
    def change_battleback(self, battleback1_name: str, battleback2_name: str) -> None:
        self._battleback1_name = battleback1_name
        self._battleback2_name = battleback2_name
    
    #--------------------------------------------------------------------------
    # * Change Parallax Background
    #--------------------------------------------------------------------------
    def change_parallax(self, name: str, loop_x: bool, loop_y: bool, sx: int, sy: int) -> None:
        self._parallax_name = name
        if self._parallax_loop_x and not loop_x:
            self._parallax_x = 0
        if self._parallax_loop_y and not loop_y:
            self._parallax_y = 0
        self._parallax_loop_x = loop_x
        self._parallax_loop_y = loop_y
        self._parallax_sx = sx
        self._parallax_sy = sy
    
    #--------------------------------------------------------------------------
    # * Update Interpreter
    #--------------------------------------------------------------------------
    def update_interpreter(self) -> None:
        while True:
            self._interpreter.update()
            if self._interpreter.running():
                return
            if self._interpreter.event_id > 0:
                self.unlock_event(self._interpreter.event_id)
                self._interpreter.clear()
            if not self.setup_starting_event():
                return
    
    #--------------------------------------------------------------------------
    # * Unlock Event
    #--------------------------------------------------------------------------
    def unlock_event(self, event_id: int) -> None:
        if event_id in self._events:
            self._events[event_id].unlock()
    
    #--------------------------------------------------------------------------
    # * Starting Event Setup
    #--------------------------------------------------------------------------
    def setup_starting_event(self) -> bool:
        if self._need_refresh:
            self.refresh()
        if self._interpreter.setup_reserved_common_event():
            return True
        if self.setup_starting_map_event():
            return True
        if self.setup_autorun_common_event():
            return True
        return False
    
    #--------------------------------------------------------------------------
    # * Determine Existence of Starting Map Event
    #--------------------------------------------------------------------------
    def any_event_starting(self) -> bool:
        return any(event.starting for event in self._events.values())
    
    #--------------------------------------------------------------------------
    # * Detect/Set Up Starting Map Event
    #--------------------------------------------------------------------------
    def setup_starting_map_event(self) -> Optional[Any]:
        event = next((event for event in self._events.values() if event.starting), None)
        if event:
            event.clear_starting_flag()
            self._interpreter.setup(event.list, event.id)
        return event
    
    #--------------------------------------------------------------------------
    # * Detect/Set Up Autorun Common Event
    #--------------------------------------------------------------------------
    def setup_autorun_common_event(self) -> Optional[Any]:
        event = next((event for event in JRPG.data.common_events 
                     if event and event.autorun() and JRPG.objects.switches.get(event.switch_id)), None)
        if event:
            self._interpreter.setup(event.list)
        return event