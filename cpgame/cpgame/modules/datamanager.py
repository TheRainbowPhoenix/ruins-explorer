# cpgame/modules/datamanager.py
# A dynamic data manager for loading and unloading game data modules on the fly.

import sys
import gc

try:
    from typing import Optional, Any, Dict, List, Union
except:
    pass

def _get_public_attributes(module: Any) -> List[str]:
    """Inspects a module and returns a list of its public data attributes."""
    # A simple heuristic for MicroPython: public data is all-caps.
    # This avoids pulling in imports or private variables.
    public_attrs = []
    # Use dir() which is available on MicroPython modules
    for attr_name in dir(module):
        if not attr_name.startswith('_'):
            is_upper = True
            # Check if the attribute name is entirely uppercase
            for char in attr_name:
                if 'a' <= char <= 'z':
                    is_upper = False
                    break
            if is_upper:
                public_attrs.append(attr_name)
    return public_attrs

def _cleanup_module(mod_name: str, mod: Any):
    """Safely cleans up and unloads a module to free memory."""
    if mod:
        # Dynamically find public attributes to delete
        public_attrs = _get_public_attributes(mod)
        for attr_name in public_attrs:
            if hasattr(mod, attr_name):
                try:
                    delattr(mod, attr_name)
                except:
                    pass
    
    # Uncache the module so it can be garbage collected
    if mod_name in sys.modules:
        try:
            sys.modules.pop(mod_name)
        except:
            pass
    
    # Drop the reference and run garbage collection
    try:
        del mod
    except:
        pass
    gc.collect()

class DataProxy:
    """A context manager to safely load and automatically clean up a data object."""
    def __init__(self, loader_func, object_name: str):
        self._load = loader_func
        self._object_name = object_name
        self._instance = None

    def __enter__(self):
        self._instance = self._load(self._object_name)
        return self._instance

    def __exit__(self, exc_type, exc_val, exc_tb):
        # The actual module cleanup is handled by the ModuleProxy.
        # This just ensures the loaded data object itself is dereferenced.
        del self._instance
        gc.collect()

def _title_case(s: str) -> str:
    """Mimics str.title() for MicroPython: capitalizes first char, lowercases the rest."""
    if not s or len(s) <= 1:
        return s
    return s[0].upper() + s[1:].lower()

class DataObject:
    """A lightweight wrapper that provides attribute-style access to a dictionary."""
    def __init__(self, data_dict: Dict):
        # Store the dictionary internally. Don't use __dict__.update() to avoid method name collisions and keep it memory-light.
        self._data = data_dict

    def _to_camel_case(self, snake_str: str) -> str:
        """Converts snake_case_string to camelCaseString."""
        parts = snake_str.split('_')
        if len(parts) > 1:
            return parts[0] + "".join(_title_case(x) for x in parts[1:])
        return snake_str

    def __getattr__(self, name: str) -> Any:
        """
        Provides attribute access, e.g., obj.actor_id.
        """
        # check if the key exists as is (e.g., 'party_members')
        if name in self._data:
            return self._data[name]
        
        # try converting the requested snake_case name to camelCase
        camel_name = self._to_camel_case(name)
        if camel_name in self._data:
            return self._data[camel_name]

        raise AttributeError("'DataObject' has no attribute '{}'".format(name))
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Gets a value from the dictionary, with snake_case to camelCase fallback.
        Mirrors the behavior of dict.get().
        """
        if key in self._data:
            return self._data[key]
        
        camel_key = self._to_camel_case(key)
        if camel_key in self._data:
            return self._data[camel_key]
            
        return default

    def keys(self):
        """Returns the original keys of the underlying dictionary."""
        return self._data.keys()

    def values(self):
        """Returns the original values of the underlying dictionary."""
        return self._data.values()

    def items(self):
        """Returns the original (key, value) pairs of the underlying dictionary."""
        return self._data.items()

    def __repr__(self) -> str:
        return "DataObject({})".format(repr(self._data))

class ModuleProxy:
    """
    Acts as a proxy for a data module (e.g., actors.py).
    It loads the module's HEADER on creation and provides methods to load
    individual objects from it on demand, with cleanup.
    """
    def __init__(self, data_category: str):
        self.category = data_category
        self.module_path = "cpgame.game_data." + self.category
        self.name_id = self.category.upper() + "_" # HACK: to avoid the "id" int. Should be removed later.
        self._module = None
        self._header = None
        self._load_header()

    def _load_header(self):
        """Loads only the HEADER from the module to see what's available."""
        mod = None
        try:
            mod = __import__(self.module_path, None, None, ('HEADER',))
            self._header = mod.HEADER
        except (ImportError, AttributeError):
            print("DataManager Error: Could not load HEADER from", self.module_path)
            self._header = {'exports': []}
        finally:
            if mod:
                _cleanup_module(self.module_path, mod)

    def _load_object_from_module(self, object_name: str):
        """Loads the full module to retrieve a specific object."""
        if not self._header:
            raise AttributeError("Module '{}' is missing HEADER".format(self.module_path))
        if object_name not in self._header.get('exports', []):
            raise AttributeError("Object '{}' not found in '{}'".format(object_name, self.category))
        
        try:
            # Import the module to get the specific object
            self._module = __import__(self.module_path, None, None, (object_name,))
            # return getattr(self._module, object_name)
            data = getattr(self._module, object_name)
            # Inject the category metadata into the loaded data
            if isinstance(data, dict):
                data['__name__'] = self.category
                return DataObject(data)
            elif isinstance(data, list):
                return [DataObject(item) if isinstance(item, dict) else item for item in data]
            return data
            
        except (ImportError, AttributeError) as e:
            raise ImportError("DataManager Error: Failed to load '{}' from {}".format(object_name, self.module_path))
            return None
    
    def _resolve_name(self, object_id: int):
        """ HACK: To convert int ID to strings to be imported from data """
        return "{}_{}".format(self.name_id, object_id)

    def get(self, object_name: Union[str, int]) -> Optional[Any]:
        """
        Gets a specific data object. NOTE: This does not auto-cleanup memory.
        Use `load()` with a `with` statement for better memory management.
        """
        if type(object_name) == int:
            object_name = self._resolve_name(object_name)
        return self._load_object_from_module(str(object_name))

    def load(self, object_name: Union[str, int]) -> DataProxy:
        """
        Provides a context manager for safe loading/unloading of a data object.
        Usage: with data_manager.actors.load("hero") as actor_data: ...
        """
        if type(object_name) == int:
            object_name = self._resolve_name(object_name)
        return DataProxy(self._load_object_from_module, str(object_name))
    
    def exists(self, object_name: Union[str, int]) -> bool:
        """
        Check if a specific data object exists in the module's exports.
        This method only checks the HEADER, no actual loading occurs.
        """
        if not self._header:
            return False
        if type(object_name) == int:
            object_name = self._resolve_name(object_name)
        return object_name in self._header.get('exports', [])
    
    def all(self) -> Dict[str, Any]:
        """
        Loads all exported objects from the module and returns them as a dictionary.
        NOTE: This does not auto-cleanup memory. Use with caution on memory-constrained systems.
        """
        if not self._header:
            return {}
        
        result = {}
        exports = self._header.get('exports', [])
        
        # Import the entire module once to get all objects
        try:
            self._module = __import__(self.module_path, None, None, tuple(exports))
            
            for object_name in exports:
                try:
                    data = getattr(self._module, object_name)
                    # Inject the category metadata into the loaded data
                    if isinstance(data, dict):
                        data['__name__'] = self.category
                    result[object_name] = data
                except AttributeError:
                    # Skip objects that can't be found
                    pass
                    
        except ImportError:
            print("DataManager Error: Failed to load module for all() method:", self.module_path)
            
        return result

    def __del__(self):
        """Ensures the loaded module is cleaned up when the proxy is destroyed."""
        if self._module:
            _cleanup_module(self.module_path, self._module)

class DataManager:
    """
    A central manager for accessing game data through proxy objects.
    This approach minimizes memory usage by only loading data as needed.
    """
    def __init__(self):
        self.actors        = ModuleProxy("actors")
        self.classes       = ModuleProxy("classes")
        self.skills        = ModuleProxy("skills")
        self.items         = ModuleProxy("items")
        self.weapons       = ModuleProxy("weapons")
        self.armors        = ModuleProxy("armors")
        self.enemies       = ModuleProxy("enemies")
        self.troops        = ModuleProxy("troops")
        self.states        = ModuleProxy("states")
        self.animations    = ModuleProxy("animations")
        self.tilesets      = ModuleProxy("tilesets")
        self.common_events = ModuleProxy("common_events")
        self.system        = ModuleProxy("system")
        self.mapinfos      = ModuleProxy("mapinfos")
    
    def init(self):
        self.setup_battle_test() # TODO
    
    def setup_battle_test(self):
        from cpgame.systems.jrpg import JRPG
        if JRPG.objects and JRPG.objects.party:
            JRPG.objects.party.setup_battle_test()