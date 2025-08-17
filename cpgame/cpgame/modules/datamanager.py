# cpgame/modules/datamanager.py
# A dynamic data manager for loading and unloading game data modules on the fly.
import sys
import gc

try:
    from typing import Optional, Any, Dict, List
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

class ModuleProxy:
    """
    Acts as a proxy for a data module (e.g., actors.py).
    It loads the module's HEADER on creation and provides methods to load
    individual objects from it on demand, with cleanup.
    """
    def __init__(self, data_category: str):
        self.category = data_category
        self.module_path = "cpgame.game_data." + self.category
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
            return getattr(self._module, object_name)
        except (ImportError, AttributeError) as e:
            raise ImportError("DataManager Error: Failed to load '{}' from {}".format(object_name, self.module_path))
            return None

    def get(self, object_name: str) -> Optional[Any]:
        """
        Gets a specific data object. NOTE: This does not auto-cleanup memory.
        Use `load()` with a `with` statement for better memory management.
        """
        return self._load_object_from_module(object_name)

    def load(self, object_name: str) -> DataProxy:
        """
        Provides a context manager for safe loading/unloading of a data object.
        Usage: with data_manager.actors.load("hero") as actor_data: ...
        """
        return DataProxy(self._load_object_from_module, object_name)

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
        self.actors = ModuleProxy("actors")
        # In the future, you can add more data categories here:
        # self.items = ModuleProxy("items")
        # self.enemies = ModuleProxy("enemies")