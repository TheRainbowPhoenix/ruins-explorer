# cpgame/game_objects/message.py
# This class handles the state of the message window.

try:
    from typing import Optional
except:
    pass

class GameMessage:
    """Holds the data for the message being displayed."""
    def __init__(self):
        self.clear()

    def clear(self):
        self._texts: list[str] = []
        self.face_name = ""
        self.face_index = 0
        self.background = 0
        self.position = 2 # 0:top, 1:middle, 2:bottom

        # For input windows
        self._number_input_variable_id: Optional[int] = None
        self._number_input_digits_max: int = 0

        self._name_input_actor_id: Optional[int] = None
        self._name_input_max_chars = 0
    
    def add(self, text: str):
        self._texts.append(text)
        
    def is_busy(self) -> bool:
        return self.is_text() or self.is_number_input() or self.is_name_input()
    
    def is_text(self) -> bool:
        return len(self._texts) > 0
    
    def is_number_input(self) -> bool:
        return self._number_input_variable_id is not None
    
    def is_name_input(self):
        return self._name_input_actor_id is not None
    
    def start_number_input(self, var_id: int, digits: int):
        self._number_input_variable_id = var_id
        self._number_input_digits_max = digits
    
    def start_name_input(self, actor_id, max_chars):
        self._name_input_actor_id, self._name_input_max_chars = actor_id, max_chars

    @property
    def number_input_variable_id(self) -> Optional[int]:
        return self._number_input_variable_id

    @property
    def number_input_digits_max(self) -> int:
        return self._number_input_digits_max
    
    @property
    def name_input_actor_id(self):
        return self._name_input_actor_id

    @property
    def name_input_max_chars(self):
        return self._name_input_max_chars

    @property
    def texts(self) -> list[str]:
        return self._texts
