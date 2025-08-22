# engine/asset.py
# A central manager to load and process all game data.

# from cpgame.engine.animation import AnimationFrame
# from cpgame.game_assets import templar_data
# from cpgame.game_assets import jrpg_data
# from cpgame.game_assets.fanta_tiles import image as fanta_tileset_img # Your raw JRPG tileset image

# from cpgame.engine.profiler import MemoryProfiler

from cpgame.game_assets import fanta_tiles

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
        
        # if tileset:
        #     self._cache[name] = tileset
        return tileset

    def unload(self, name: str):
        """Unloads a specific asset and its source module from memory."""
        # if name in self._cache:
        #     del self._cache[name]
        
        # This is a simplified cleanup; a real system would track dependencies.
        if name == "jrpg":
            from cpgame.modules.datamanager import _cleanup_module
            if 'fanta_tiles' in self._loaded_modules:
                _cleanup_module('cpgame.game_assets.fanta_tiles', self._loaded_modules.pop('fanta_tiles'))
            if 'jrpg_data' in self._loaded_modules:
                _cleanup_module('cpgame.game_assets.jrpg_data', self._loaded_modules.pop('jrpg_data'))
        
        import gc
        gc.collect()