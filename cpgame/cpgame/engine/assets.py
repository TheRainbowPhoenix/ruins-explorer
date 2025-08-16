# engine/asset.py
# A central manager to load and process all game data.

from cpgame.engine.animation import AnimationFrame
from cpgame.game_assets import templar_data
from cpgame.game_assets import jrpg_data
from cpgame.game_assets.fanta_tiles import image as fanta_tileset_img # Your raw JRPG tileset image

try:
    from typing import Optional, List, Dict
except:
    pass

class Tilemap:
    def __init__(self, img, tileboxes, solid_ids):
        self.img = img
        self.tileboxes = tileboxes
        self.solid = solid_ids

class AssetManager:
    """
    A singleton class that loads all assets once at the start of the game.
    This mimics Phaser's loader, but pre-loads everything for simplicity.
    """
    def __init__(self):
        self.animations: Dict[str, List[AnimationFrame]] = {}
        self.tilesets: Dict[str, Tilemap] = {} # tilemap
        self.maps: Dict[str, Dict] = {}
        self.is_loaded = False

    def load_all(self):
        """Processes all raw asset data into usable game objects."""
        if self.is_loaded: return
        print("AssetManager: Loading all assets...")

        # TODO: use PAK if successful, and make it a PAK loader
        # TODO: else, use the class loader with cleanup

        # --- Load Templar Assets ---
        for name, data in templar_data.sprites.items(): # type: ignore
            self.animations[name] = [AnimationFrame(*frame) for frame in data]
        for name, data in templar_data.bounce.items(): # type: ignore
            self.animations[name] = [AnimationFrame(*frame) for frame in data]
        self.tilesets["templar"] = Tilemap(*templar_data.tileset) # type: ignore

        # --- Load JRPG Assets ---
        self.tilesets["jrpg"] = Tilemap(fanta_tileset_img, [], jrpg_data.solid_tiles) # type: ignore
        self.maps["jrpg_village"] = {
            "layout": jrpg_data.map_layout, # type: ignore
            "objects": jrpg_data.map_objects, # type: ignore
            "signs": jrpg_data.map_signs # type: ignore
        }
        
        self.is_loaded = True
        print("AssetManager: Load complete.")