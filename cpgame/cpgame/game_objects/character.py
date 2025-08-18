# cpgame/game_objects/character.py
# Contains the class hierarchy for map characters (GameCharacterBase, GameCharacter, GamePlayer)

from cpgame.engine.geometry import Vec2

class GameCharacterBase:
    """
    Base class for map characters. Manages position, graphics, and basic movement state.
    """
    def __init__(self):
        self.x: int = 0
        self.y: int = 0
        self.real_x: float = 0.0
        self.real_y: float = 0.0
        
        self.character_name: str = ""
        self.character_index: int = 0
        
        self.move_speed: int = 4
        self.direction: int = 2  # 2:down, 4:left, 6:right, 8:up
        
        self._moving = False

    def is_moving(self) -> bool:
        return self._moving

    def update(self):
        # In a full implementation, this would update movement interpolation
        # between (x, y) and (real_x, real_y)
        pass

    def moveto(self, x: int, y: int):
        self.x = x
        self.y = y
        self.real_x = float(x)
        self.real_y = float(y)


class GameCharacter(GameCharacterBase):
    """
    Inherits from CharacterBase and adds more complex movement logic.
    """
    def __init__(self):
        super(GameCharacter, self).__init__()
        # Logic for move routes, etc., would go here.

    def move_straight(self, d: int):
        # Simplified movement for demonstration
        dx, dy = 0, 0
        if d == 2: dy = 1
        elif d == 4: dx = -1
        elif d == 6: dx = 1
        elif d == 8: dy = -1
        
        if dx != 0 or dy != 0:
            self.moveto(self.x + dx, self.y + dy)
            self._moving = True
        else:
            self._moving = False


class GamePlayer(GameCharacter):
    """
    The player character. Inherits from GameCharacter and handles input.
    """
    def __init__(self):
        super(GamePlayer, self).__init__()
    
    # The actual player logic is currently handled directly in JRPGScene,
    # but this class provides the correct hierarchy for future expansion.
    def update(self):
        # Player-specific updates would go here
        super(GamePlayer, self).update()

    def refresh(self):
        pass # TODO