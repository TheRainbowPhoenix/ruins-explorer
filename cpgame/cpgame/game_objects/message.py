# cpgame/game_objects/message.py
# This class handles the state of the message window.

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
    
    def add(self, text: str):
        self._texts.append(text)
        
    def is_busy(self) -> bool:
        return len(self._texts) > 0

    @property
    def texts(self) -> list[str]:
        return self._texts
