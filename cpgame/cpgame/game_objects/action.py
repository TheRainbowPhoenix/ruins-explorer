# cpgame/game_objects/action.py
# Contains classes related to battle actions and their results.

try:
    from typing import List, Any, Optional
except:
    pass

class GameActionResult:
    """Holds the results of a battle action, like damage, state changes, etc."""
    def __init__(self, battler):
        """
        Object Initialization
        
        :param battler: The battler this result belongs to
        """
        self._battler = battler
        self.clear()
    
    def clear(self):
        """Clear - Resets all action results to their default state."""
        self.clear_hit_flags()
        self.clear_damage_values()
        self.clear_status_effects()
    
    def clear_hit_flags(self):
        """Clear Hit Flags"""
        self.used = False        # used flag
        self.missed = False      # missed flag
        self.evaded = False      # evaded flag
        self.critical = False    # critical flag
        self.success = False     # success flag
    
    def clear_damage_values(self):
        """Clear Damage Values"""
        self.hp_damage = 0       # HP damage
        self.mp_damage = 0       # MP damage
        self.tp_damage = 0       # TP damage
        self.hp_drain = 0        # HP drain
        self.mp_drain = 0        # MP drain
    
    def clear_status_effects(self):
        """Clear Status Effects - Clears only the status-related results."""
        self.added_states = []        # added states
        self.removed_states = []      # removed states
        self.added_buffs = []         # added buffs
        self.added_debuffs = []       # added debuffs
        self.removed_buffs = []       # removed buffs/debuffs
    
    def make_damage(self, value: int, item):
        """
        Create Damage
        
        :param value: Damage value
        :param item: Item/skill that caused the damage
        """
        if value == 0:
            self.critical = False
        
        if hasattr(item.damage, 'to_hp') and item.damage.to_hp:
            self.hp_damage = value
        
        if hasattr(item.damage, 'to_mp') and item.damage.to_mp:
            self.mp_damage = value
            # Would be: self.mp_damage = min(self._battler.mp, self.mp_damage)
        
        if hasattr(item.damage, 'drain') and item.damage.drain:
            self.hp_drain = self.hp_damage
            self.mp_drain = self.mp_damage
            # Would be: 
            # self.hp_drain = min(self._battler.hp, self.hp_drain)
        
        if (hasattr(item.damage, 'to_hp') and item.damage.to_hp) or self.mp_damage != 0:
            self.success = True
    
    def added_state_objects(self) -> List[Any]:
        """
        Get Added States as an Object Array
        
        :return: List of state objects
        """
        # Would be: return [self.data_states[id] for id in self.added_states]
        return []
    
    def removed_state_objects(self) -> List[Any]:
        """
        Get Removed States as an Object Array
        
        :return: List of state objects
        """
        # Would be: return [self.data_states[id] for id in self.removed_states]
        return []
    
    def status_affected(self) -> bool:
        """
        Determine Whether Some Sort of Status (Parameter or State) Was Affected
        
        :return: True if status was affected
        """
        return not (not self.added_states and not self.removed_states and
                   not self.added_buffs and not self.added_debuffs and 
                   not self.removed_buffs)
    
    def hit(self) -> bool:
        """
        Determine Final Hit
        
        :return: True if hit was successful
        """
        return self.used and not self.missed and not self.evaded
    
    def hp_damage_text(self) -> str:
        """
        Get Text for HP Damage
        
        :return: Formatted damage text
        """
        # Would use Vocab system in full implementation
        if self.hp_drain > 0:
            fmt = " drains %s %d!"  # Vocab::ActorDrain or Vocab::EnemyDrain
            return fmt % ("HP", self.hp_drain)
        elif self.hp_damage > 0:
            fmt = " takes %d damage!"  # Vocab::ActorDamage or Vocab::EnemyDamage
            return fmt % self.hp_damage
        elif self.hp_damage < 0:
            fmt = " recovers %s %d!"  # Vocab::ActorRecovery or Vocab::EnemyRecovery
            return fmt % ("HP", -self.hp_damage)
        else:
            fmt = " takes no damage!"  # Vocab::ActorNoDamage or Vocab::EnemyNoDamage
            return fmt
    
    def mp_damage_text(self) -> str:
        """
        Get Text for MP Damage
        
        :return: Formatted damage text
        """
        # Would use Vocab system in full implementation
        if self.mp_drain > 0:
            fmt = " drains %s %d!"  # Vocab::ActorDrain or Vocab::EnemyDrain
            return fmt % ("MP", self.mp_drain)
        elif self.mp_damage > 0:
            fmt = " loses %s %d!"  # Vocab::ActorLoss or Vocab::EnemyLoss
            return fmt % ("MP", self.mp_damage)
        elif self.mp_damage < 0:
            fmt = " recovers %s %d!"  # Vocab::ActorRecovery or Vocab::EnemyRecovery
            return fmt % ("MP", -self.mp_damage)
        else:
            return ""
    
    def tp_damage_text(self) -> str:
        """
        Get Text for TP Damage
        
        :return: Formatted damage text
        """
        # Would use Vocab system in full implementation
        if self.tp_damage > 0:
            fmt = " loses %s %d!"  # Vocab::ActorLoss or Vocab::EnemyLoss
            return fmt % ("TP", self.tp_damage)
        elif self.tp_damage < 0:
            fmt = " gains %s %d!"  # Vocab::ActorGain or Vocab::EnemyGain
            return fmt % ("TP", -self.tp_damage)
        else:
            return ""
class GameAction:
    """
    Represents a single action (attack, skill, item) to be taken by a battler.
    """
    def __init__(self, subject):
        self.subject = subject
        self.clear()

    def clear(self):
        self._item = None
        self._target_index = -1

    def item(self):
        return self._item