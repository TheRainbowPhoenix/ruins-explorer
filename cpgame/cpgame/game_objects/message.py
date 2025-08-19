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

        self._choices: list[str] = []
        self._choice_cancel_type = 0
        self._choice_callback = None
        self._choice_variable_id: Optional[int] = None
    
    def add(self, text: str):
        self._texts.append(text)
        
    def is_busy(self) -> bool:
        return self.is_text() or self.is_number_input() or self.is_name_input() or self.is_choice()
    
    def is_text(self) -> bool:
        return len(self._texts) > 0
    
    def is_number_input(self) -> bool:
        return self._number_input_variable_id is not None
    
    def is_name_input(self):
        return self._name_input_actor_id is not None

    def is_choice(self) -> bool:
        return len(self._choices) > 0
    
    def start_number_input(self, var_id: int, digits: int):
        self._number_input_variable_id = var_id
        self._number_input_digits_max = digits
    
    def start_name_input(self, actor_id, max_chars):
        self._name_input_actor_id = actor_id
        self._name_input_max_chars = max_chars

    def start_choice(self, choices: list[str], cancel_type: int, callback = None, var_id: Optional[int]=None):
        self._choice_variable_id = var_id
        self._choice_cancel_type = cancel_type
        self._choices = choices
        self._choice_callback = callback
    
    @property
    def choices(self) -> list[str]:
        return self._choices

    @property
    def choice_cancel_type(self):
        return self._choice_cancel_type

    @property
    def choice_variable_id(self) -> Optional[int]:
        return self._choice_variable_id

    @property
    def choice_callback(self):
        return self._choice_callback

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
