# cpgame/game_objects/event.py
# This class handles map events, including page switching and triggers.

from cpgame.game_objects.character import GameCharacter
from cpgame.systems.jrpg import JRPG

try:
    from typing import Dict, Any, List, Optional
except:
    pass

class GameEvent(GameCharacter):
    """Manages a single event on the map, including its pages and triggers."""
    def __init__(self, map_id: int, event_data: Dict):
        super(GameEvent, self).__init__()
        self._map_id = map_id
        self._event_data = event_data
        self.id = event_data.get('id', 0)
        
        self._erased = False
        self._starting = False
        self._active_page = None
        
        self.moveto(event_data.get('x', 0), event_data.get('y', 0))
        self.refresh()

    def start(self):
        """Flags the event to start running on the next update."""
        if self._active_page and self._active_page.get('list'):
            self._starting = True

    def refresh(self):
        """Finds the correct event page to display and sets it up."""
        new_page = self._find_proper_page()
        if self._active_page != new_page:
            self.setup_page(new_page)
    
    def _find_proper_page(self) -> Optional[Dict]:
        """Iterates through pages in reverse to find the first valid one."""
        if self._erased:
            return None
        
        for page in reversed(self._event_data.get('pages', [])):
            if self._conditions_met(page):
                return page
        return None

    def _conditions_met(self, page: Dict) -> bool:
        """Checks if the conditions for an event page are met."""
        # TODO: This is a placeholder for a full condition system (switches, variables, etc.)
        # For now, all pages are considered valid.
        return True

    def setup_page(self, page: Optional[Dict]):
        """Sets the event's properties based on the active page."""
        self._active_page = page
        if page:
            graphic = page.get('graphic', {})
            self.character_name = graphic.get('characterName', "")
            self.character_index = graphic.get('characterIndex', 0)
            self.tile_id = graphic.get('tileId', 0)
            self.direction = graphic.get('direction', 2)
        else:
            self.tile_id = 0
            self.character_name = ""

    def update(self):
        """Updates the event, starting its interpreter if flagged."""
        super(GameEvent, self).update()
        if self._starting:
            # If this event is starting, ask the map's interpreter to run its list
            if JRPG.objects and JRPG.objects.map:
                JRPG.objects.map.start_event_interpreter(self)
            self._starting = False

    @property
    def command_list(self) -> List:
        return self._active_page.get('list', []) if self._active_page else []