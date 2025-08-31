# engine/asset.py
# A central manager to load and process all game data.

from cpgame.engine.animation import AnimationFrame, Animation
from cpgame.engine.logger import log

try:
    from typing import Optional, Dict, Any, Set, List, Tuple, Union
except:
    pass


class Tilemap:
    def __init__(self, img: Any, tileboxes, solid_ids: Set[int]):
        self.img = img
        self.tileboxes = tileboxes
        self.solid = solid_ids

class VariantManager:
    """Manages image variants (flipped, rotated, etc.)"""
    def __init__(self):
        self.variants: Dict[str, Any] = {}
    
    def register_variant(self, name: str, image: Any):
        """Register an image variant with a name."""
        self.variants[name] = image
    
    def get_variant(self, name: str) -> Optional[Any]:
        """Get a registered variant by name."""
        return self.variants.get(name)

class AssetManager:
    """An on-demand loader for game assets."""
    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._loaded_modules: Dict[str, Any] = {}
        self._variants = VariantManager()

    def tileset(self, asset_name: str, elements: Union[str, Tuple[str, str, str]], base_path: str = "cpgame.game_assets") -> Optional[Tilemap]:
        """
        Load a tileset dynamically from specified module and elements.
        
        Args:
            asset_name: Name of the asset module (e.g., "templar_data")
            elements: Either a single element name or tuple of 3 element names
                     (image, tileboxes, solid_ids)
            base_path: Base import path (default: "cpgame.game_assets")
        
        Returns:
            Tilemap instance or None if failed
        """
        cache_key = f"tileset_{base_path}.{asset_name}.{str(elements)}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        log(f"AssetManager: Loading tileset '{asset_name}' from '{base_path}'...")
        
        try:
            # Dynamic import
            module_path = f"{base_path}.{asset_name}"
            module = __import__(module_path, None, None, ('',))
            self._loaded_modules[asset_name] = module
            
            if isinstance(elements, tuple) and len(elements) == 3:
                # Load tuple of 3 elements
                img_attr, boxes_attr, solid_attr = elements
                img = getattr(module, img_attr)
                tileboxes = getattr(module, boxes_attr)
                solid_ids = getattr(module, solid_attr)
                tileset = Tilemap(img, tileboxes, solid_ids)
            else:
                # Load single element (assuming it's a tuple/list like templar_data.tileset)
                data = getattr(module, elements)
                tileset = Tilemap(*data)
            
            self._cache[cache_key] = tileset
            return tileset
            
        except (ImportError, AttributeError) as e:
            log(f"AssetManager: Failed to load tileset '{asset_name}': {e}")
            return None

    def animation(self, asset_name: str, animation_identifier: Union[str, Dict[str, List], List[Tuple]], base_path: str = "cpgame.game_assets", frame_rate: float = 24.0) -> Optional[Union[Dict[str, Animation], Animation]]:
        """
        Load animations dynamically from specified module.
        
        Args:
            asset_name: Name of the asset module (e.g., "templar_data")
            animation_identifier: Either:
                - String name of consolidated dict (e.g., "sprites")
                - Direct dict mapping animation names to frame data
                - List of tuples for single animation frames
            base_path: Base import path (default: "cpgame.game_assets")
            frame_rate: Default frame rate for animations
        """
        # Create cache key based on identifier type
        if isinstance(animation_identifier, str):
            cache_key = f"animation_{base_path}.{asset_name}.{animation_identifier}"
        elif isinstance(animation_identifier, dict):
            cache_key = f"animation_{base_path}.{asset_name}.dict_{hash(str(sorted(animation_identifier.keys())))}"
        else:  # List/tuple
            cache_key = f"animation_{base_path}.{asset_name}.list_{len(animation_identifier)}"
            
        if cache_key in self._cache:
            return self._cache[cache_key]

        log(f"AssetManager: Loading animations from '{asset_name}'...")
        
        try:
            if isinstance(animation_identifier, list):
                # Single animation from list of tuples
                frames = []
                for frame_data in animation_identifier:
                    if len(frame_data) == 8:
                        # (img, imgH, x, y, w, h, cx, cy, duration)
                        img, src_x, src_y, width, height, pivot_x, pivot_y, duration = frame_data
                        # img, imgH, x, y, w, h, cx, cy, duration = frame_data
                        # Use imgH for flipped frames, img for normal
                        # The decision of which to use is made at animation creation time
                        # frame_img = img # imgH if imgH else img  # Fallback to img if imgH not available
                        frame = AnimationFrame(img, src_x, src_y, width, height, pivot_x, pivot_y, duration)
                        frames.append(frame)
                
                if frames:
                    anim = Animation("custom", frames, frame_rate)
                    self._cache[cache_key] = anim
                    return anim
                else:
                    return None
            
            elif isinstance(animation_identifier, str):
                # Load from module attribute (consolidated dict like "sprites")
                module_path = f"{base_path}.{asset_name}"
                module = __import__(module_path, None, None, ('',))
                self._loaded_modules[asset_name] = module
                animation_dict = getattr(module, animation_identifier)
            else:
                # Use direct dict
                animation_dict = animation_identifier
            
            # Process each animation in the dict
            animations = {}
            for anim_name, frame_data_list in animation_dict.items():
                frames = []
                for frame_data in frame_data_list:
                    if len(frame_data) == 8:
                        img, src_x, src_y, width, height, pivot_x, pivot_y, duration = frame_data
                        frame = AnimationFrame(img, src_x, src_y, width, height, pivot_x, pivot_y, duration)
                        frames.append(frame)
                
                if frames:
                    anim = Animation(anim_name, frames, frame_rate)
                    animations[anim_name] = anim
            
            if animations:
                self._cache[cache_key] = animations
                return animations
            else:
                return None
                
        except (ImportError, AttributeError) as e:
            log(f"AssetManager: Failed to load animations from '{asset_name}': {e}")
            return None

    def get_tileset(self, name: str) -> Optional[Tilemap]:
        """Loads a tileset from its module, caches it, and returns it."""
        if f"tileset_{name}" in self._cache:
            return self._cache[f"tileset_{name}"]
        
        log("AssetManager: Loading tileset '{}'...".format(name))
        
        tileset = None
        if name == "jrpg":
            pass
        elif name == "templar":
            tileset = self.tileset("templar_data", "tileset")
        
        if tileset:
            self._cache[f"tileset_{name}"] = tileset
        return tileset
    
    def get_animation(self, name: str) -> Optional[Animation]:
        """Loads a specific animation by name, caches it, and returns it."""
        if f"single_animation_{name}" in self._cache:
            return self._cache[f"single_animation_{name}"]

        log("AssetManager: Loading animation '{}'...".format(name))
        
        animation = None
        
        # Try to load from templar data
        try:
            # Load all sprites animations
            sprites_animations = self.animation("templar_data", "sprites")
            if sprites_animations and name in sprites_animations:
                animation = sprites_animations[name]
            
            # If not found, try bounce animations
            if not animation:
                bounce_animations = self.animation("templar_data", "bounce")
                if bounce_animations and name in bounce_animations:
                    animation = bounce_animations[name]
                    
        except ImportError:
            pass
        
        if animation:
            self._cache[f"single_animation_{name}"] = animation
        return animation

    def get_animations(self) -> Dict[str, Animation]:
        """Returns all currently loaded animations."""
        result = {}
        for key, value in self._cache.items():
            if key.startswith("single_animation_"):
                anim_name = key[len("single_animation_"):]
                result[anim_name] = value
        return result

    def get_variant_manager(self) -> VariantManager:
        """Get the variant manager for image variants."""
        return self._variants

    def _get_templar_animation_names(self) -> Set[str]:
        """Helper to get available templar animation names without loading data."""
        try:
            from cpgame.game_assets import templar_data
            names = set(templar_data.sprites.keys())
            names.update(templar_data.bounce.keys())
            return names
        except ImportError:
            return set()
    
    def unload(self, name: str):
        """Unloads a specific asset and its source module from memory."""
        cache_keys_to_remove = []
        for key in self._cache:
            if f"_{name}" in key or f".{name}" in key:
                cache_keys_to_remove.append(key)
        
        for key in cache_keys_to_remove:
            del self._cache[key]
        
        if name == "templar":
            from cpgame.modules.datamanager import _cleanup_module
            if 'templar_data' in self._loaded_modules:
                _cleanup_module('cpgame.game_assets.templar_data', self._loaded_modules.pop('templar_data'))
        
        import gc
        gc.collect()