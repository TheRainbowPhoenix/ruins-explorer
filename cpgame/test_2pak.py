import gint
import sys
import gc

def mem_used():
    gc.collect()
    return gc.mem_alloc()


class ModuleProxy:
    """Context manager for on-demand module/class loading and cleanup."""
    def __init__(self, module_path, class_name, *args, **kwargs):
        self.module_path = module_path
        self.class_name = class_name
        self.args = args
        self.kwargs = kwargs
        self.instance = None
        self.module = None

    def __enter__(self):
        # Import module dynamically
        try:
            self.module = __import__(self.module_path, None, None, (self.class_name,))
            target_class = getattr(self.module, self.class_name)
            # Create instance with both args and kwargs
            self.instance = target_class(*self.args, **self.kwargs)
            return self.instance
        except Exception as e:
            print(f"ModuleProxy error: {e}")
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.instance:
            if hasattr(self.instance, 'destroy'):
                self.instance.destroy()
            del self.instance

        if self.module:
            # Clean up module attributes
            module_name = self.module_path
            if hasattr(self.module, '__dict__'):
                attrs = list(self.module.__dict__.keys())
                for attr in attrs:
                    if not attr.startswith('__'):
                        try:
                            delattr(self.module, attr)
                        except:
                            pass

            # Remove from sys.modules
            if module_name in sys.modules:
                try:
                    sys.modules.pop(module_name)
                except:
                    pass

            del self.module

        gc.collect()

# Lazy-loaded PakProxy instance

# Helpers: 160B
# def draw_from(x, y, pak_name, name_prefix, max_width=320):
#     """Draw tiles from a PAK file that match a name prefix"""
#     return _get_pakloader().draw_from(x, y, pak_name, name_prefix, max_width)

# def draw_single(x, y, pak_name, entry_name):
#     """Draw a single entry by exact name"""
#     return _get_pakloader().draw_single(x, y, pak_name, entry_name)

# def list_entries(pak_name, prefix=None):
#     """List entries in a PAK file"""
#     return _get_pakloader().list_entries(pak_name, prefix)

# def clear_cache():
#     """Clear the PAK loader cache"""
#     if _pakloader is not None:
#         _get_pakloader().clear_cache()

# Example usage function
def test_pak_loader():
    """Test the PAK loader functionality"""

    with ModuleProxy('cpgame.modules.pakloader', 'PakProxy') as pak_proxy:
        
        mem_before = mem_used()
        print("PAK Loader Test")
        print("Memory before: {} bytes".format(mem_before))
        
        # List entries in tiles.pak
        count = pak_proxy.list_entries('faces.pak', 'ylva_angry')
        print("Found {} profile entries".format(count))
        
        # Draw profile entries
        if count > 0:
            pak_proxy.draw_from(20, 60, 'faces.pak', 'ylva_angry', 96+20)
            gint.getkey()
            pak_proxy.draw_from(20, 60, 'faces.pak', 'ylva_happy', 96+20)
            gint.getkey()
            pak_proxy.draw_from(20, 60, 'faces.pak', 'ylva_ok', 96+20)
            gint.getkey()
            pak_proxy.draw_from(20, 60, 'faces.pak', 'ylva_sad', 96+20)
            gint.getkey()
            pak_proxy.draw_from(20, 60, 'faces.pak', 'ylva_shocked', 96+20)
            gint.getkey()
            pak_proxy.draw_from(0, 0, 'faces.pak', 'logo', 192)
            # print("Drew {} profile entries".format(drawn))
        
        # Wait for keypress
        gint.getkey()
        # Cleanup
        pak_proxy.clear_cache()
        
        mem_after = mem_used()
        print("Memory after: {} bytes".format(mem_after))
        print("Memory used: {} bytes".format(mem_after - mem_before))
        
        gc.collect()
    print(mem_used())

test_pak_loader()