# engine/asset.py
# A central manager to load and process all game data.

# from cpgame.engine.animation import AnimationFrame
# from cpgame.game_assets import templar_data
# from cpgame.game_assets import jrpg_data
# from cpgame.game_assets.fanta_tiles import image as fanta_tileset_img # Your raw JRPG tileset image

# from cpgame.engine.profiler import MemoryProfiler

from cpgame.game_assets import fanta_tiles
from cpgame.game_assets import chipset_basic
from cpgame.game_assets.riosma import world as riosma_world

try:
    from typing import Optional, Dict, Any, Set, List
except:
    pass

class Tilemap:
    def __init__(self, img: Any, solid_ids: Set[int]):
        self.img = img
        self.solid = solid_ids

class AssetManager:
    """An on-demand loader for game assets."""
    def __init__(self):
        # self._cache: Dict[str, Any] = {}
        self._loaded_modules: Dict[str, Any] = {}

    def get_tileset(self, name: str) -> Optional[Tilemap]:
        """Loads a tileset from its module, caches it, and returns it."""
        # if name in self._cache:
        #     return self._cache[name]

        from cpgame.engine.logger import log
        log("AssetManager: Loading tileset '{}'...".format(name))
        
        tileset = None
        if name == "jrpg":
            # Lazy import
            from cpgame.game_assets import jrpg_data
            tileset = Tilemap(fanta_tiles.image, jrpg_data.solid_tiles)
            self._loaded_modules['fanta_tiles'] = fanta_tiles
            self._loaded_modules['jrpg_data'] = jrpg_data
        
        if name == "basic":
            # TODO: make this dynamic
            from cpgame.game_assets import jrpg_data
            tileset = Tilemap(chipset_basic.tileset, jrpg_data.solid_tiles)
            self._loaded_modules['chipset_basic'] = chipset_basic
            self._loaded_modules['jrpg_data'] = jrpg_data
        
        if name == "riosma_world":
            # TODO: make this dynamic
            from cpgame.game_assets import jrpg_data
            tileset = Tilemap(riosma_world.images, [i for i in range(95) if i not in [8, 9, 10, 11, 25, 26, 27, 28, 44, 75]])
            self._loaded_modules['riosma_world'] = riosma_world
            self._loaded_modules['jrpg_data'] = jrpg_data
        
        # if tileset:
        #     self._cache[name] = tileset
        return tileset

    def unload(self, name: str):
        """Unloads a specific asset and its source module from memory."""
        # if name in self._cache:
        #     del self._cache[name]
        from cpgame.modules.datamanager import _cleanup_module

        # This is a simplified cleanup; a real system would track dependencies.
        if name == "jrpg":    
            if 'fanta_tiles' in self._loaded_modules:
                _cleanup_module('cpgame.game_assets.fanta_tiles', self._loaded_modules.pop('fanta_tiles'))
            if 'jrpg_data' in self._loaded_modules:
                _cleanup_module('cpgame.game_assets.jrpg_data', self._loaded_modules.pop('jrpg_data'))
        
        if name == "basic":
            if 'chipset_basic' in self._loaded_modules:
                _cleanup_module('cpgame.game_assets.chipset_basic', self._loaded_modules.pop('chipset_basic'))
        if name == "riosma_world":
            if 'riosma_world' in self._loaded_modules:
                _cleanup_module('cpgame.game_assets.riosma.world', self._loaded_modules.pop('riosma_world'))

        import gc
        gc.collect()