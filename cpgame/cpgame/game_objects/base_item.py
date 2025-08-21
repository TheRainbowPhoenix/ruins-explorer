# cpgame/game_objects/base_item.py
# A class that uniformly handles skills, items, weapons, and armor.

from cpgame.systems.jrpg import JRPG

try:
    from typing import Optional, Any
except:
    pass

class Game_BaseItem:
    """
    A wrapper that holds a reference to an item, weapon, or armor by its
    category and ID, allowing for lazy loading of the actual data object.
    """
    def __init__(self):
        self._category: Optional[str] = None
        self._item_id: int = 0

    def is_item(self) -> bool: return self._category == 'items'
    def is_weapon(self) -> bool: return self._category == 'weapons'
    def is_armor(self) -> bool: return self._category == 'armors'
    def is_null(self) -> bool: return self._category is None

    def get_object(self) -> Optional[Any]:
        """Lazy-loads and returns the actual data object."""
        if self.is_null() or not JRPG.data or not self._category:
            return None
        
        proxy = getattr(JRPG.data, self._category)
        if proxy:
            # Note: This is a direct, non-context-managed load.
            # It's acceptable here as item data is generally small and frequently accessed.
            with proxy.load(self._item_id) as item_data:
                return item_data
        return None

    def set_object(self, item_obj):
        """Sets the reference from a data object."""
        if item_obj:
            self._category = item_obj.get('_category')
            self._item_id = item_obj.get('id', 0)
        else:
            self._category = None
            self._item_id = 0