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
        self.clear_transfer_info()
        # Logic for move routes, etc., would go here.

    def clear_transfer_info(self):
        self.transfer_pending = False
        self.new_map_id = 0
        self.new_x = 0
        self.new_y = 0

    def reserve_transfer(self, map_id, x, y):
        self.transfer_pending = True
        self.new_map_id = map_id
        self.new_x = x
        self.new_y = y

    def perform_transfer(self):
        if self.transfer_pending:
            from cpgame.systems.jrpg import JRPG
            
            if JRPG.objects and JRPG.objects.map:
                JRPG.objects.map.setup(self.new_map_id)

                self.moveto(self.new_x, self.new_y)
                self.clear_transfer_info()
            else:
                raise Exception("Transfer failed ! Invalid JRPG.objects.map")

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

    def perform_transfer(self):
        """Updates the state in JRPG.objects for the transfer. The scene handles the rest."""
        from cpgame.systems.jrpg import JRPG
        if self.transfer_pending and JRPG.objects:
            JRPG.objects.map.setup(self.new_map_id)
            self.moveto(self.new_x, self.new_y)
            self.clear_transfer_info()

    def region_id(self) -> int:
        return 0 # TODO
    
    def make_encounter_troop_id(self) -> int:
        """
        Calculates and returns a troop ID based on the current map's
        encounter list and region ID.
        """
        from cpgame.systems.jrpg import JRPG
        
        if not JRPG.objects or not JRPG.objects.map:
            return 0
        
        encounter_list = JRPG.objects.map.encounter_list()
        if not encounter_list:
            return 0

        # Filter encounters by the player's current region
        valid_encounters = [
            enc for enc in encounter_list 
            if not enc.get('regionSet') or self.region_id() in enc.get('regionSet', [])
        ]
        
        if not valid_encounters:
            return 0

        # Calculate total weight of valid encounters
        total_weight = sum(enc.get('weight', 0) for enc in valid_encounters)
        if total_weight <= 0:
            return 0
            
        # Select a random encounter based on weight
        import random
        value = random.randint(0, total_weight - 1)
        for encounter in valid_encounters:
            value -= encounter.get('weight', 0)
            if value < 0:
                return encounter.get('troopId', 0)
        
        return 0