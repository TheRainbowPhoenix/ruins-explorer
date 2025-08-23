# cpgame/game_objects/actor.py
# Contains the class hierarchy for battlers (GameBattlerBase, GameBattler, GameActor)

try:
    from typing import Dict, Any, List, Optional, Tuple, Union, List
except:
    pass

import random
import math

from cpgame.game_objects.item import GameBaseItem
from cpgame.game_objects.action import GameAction, GameActionResult
from cpgame.systems.jrpg import JRPG

class GameBattlerBase:
    """
    Base class for any entity that can participate in battle.
    Manages core stats, parameters, and states.
    """
    
    # Constants (Features)
    FEATURE_ELEMENT_RATE  = 11              # Element Rate
    FEATURE_DEBUFF_RATE   = 12              # Debuff Rate
    FEATURE_STATE_RATE    = 13              # State Rate
    FEATURE_STATE_RESIST  = 14              # State Resist
    FEATURE_PARAM         = 21              # Parameter
    FEATURE_XPARAM        = 22              # Ex-Parameter
    FEATURE_SPARAM        = 23              # Sp-Parameter
    FEATURE_ATK_ELEMENT   = 31              # Atk Element
    FEATURE_ATK_STATE     = 32              # Atk State
    FEATURE_ATK_SPEED     = 33              # Atk Speed
    FEATURE_ATK_TIMES     = 34              # Atk Times+
    FEATURE_STYPE_ADD     = 41              # Add Skill Type
    FEATURE_STYPE_SEAL    = 42              # Disable Skill Type
    FEATURE_SKILL_ADD     = 43              # Add Skill
    FEATURE_SKILL_SEAL    = 44              # Disable Skill
    FEATURE_EQUIP_WTYPE   = 51              # Equip Weapon
    FEATURE_EQUIP_ATYPE   = 52              # Equip Armor
    FEATURE_EQUIP_FIX     = 53              # Lock Equip
    FEATURE_EQUIP_SEAL    = 54              # Seal Equip
    FEATURE_SLOT_TYPE     = 55              # Slot Type
    FEATURE_ACTION_PLUS   = 61              # Action Times+
    FEATURE_SPECIAL_FLAG  = 62              # Special Flag
    FEATURE_COLLAPSE_TYPE = 63              # Collapse Effect
    FEATURE_PARTY_ABILITY = 64              # Party Ability
    
    # Constants (Feature Flags)
    FLAG_ID_AUTO_BATTLE   = 0               # auto battle
    FLAG_ID_GUARD         = 1               # guard
    FLAG_ID_SUBSTITUTE    = 2               # substitute
    FLAG_ID_PRESERVE_TP   = 3               # preserve TP
    
    # Constants (Starting Number of Buff/Debuff Icons)
    ICON_BUFF_START       = 64              # buff (16 icons)
    ICON_DEBUFF_START     = 80              # debuff (16 icons)
    
    def __init__(self):
        self._hp = 0
        self._mp = 0
        self._tp = 0
        self._hidden = False
        GameBattlerBase.clear_param_plus(self)
        GameBattlerBase.clearstates(self)
        GameBattlerBase.clearbuffs(self)
    
    @property
    def hp(self): return self._hp
    @hp.setter
    def hp(self, value): 
        self._hp = value
        self.refresh()
    
    @property
    def mp(self): return self._mp
    @mp.setter
    def mp(self, value): 
        self._mp = value
        self.refresh()
    
    @property
    def tp(self): return self._tp
    @tp.setter
    def tp(self, value): 
        self._tp = max(0, min(value, self.max_tp()))
    
    # Access Method by Parameter Abbreviations
    @property
    def mhp(self): return self.param(0)     # MHP  Maximum Hit Points
    @property
    def mmp(self): return self.param(1)     # MMP  Maximum Magic Points
    @property
    def atk(self): return self.param(2)     # ATK  ATtacK power
    @property
    def defe(self): return self.param(3)    # DEF  DEFense power ('def' is a keyword)
    @property
    def mat(self): return self.param(4)     # MAT  Magic ATtack power
    @property
    def mdf(self): return self.param(5)     # MDF  Magic DeFense power
    @property
    def agi(self): return self.param(6)     # AGI  AGIlity
    @property
    def luk(self): return self.param(7)     # LUK  LUcK
    
    # Ex-Parameters
    @property
    def hit(self): return self.xparam(0)    # HIT  HIT rate
    @property
    def eva(self): return self.xparam(1)    # EVA  EVAsion rate
    @property
    def cri(self): return self.xparam(2)    # CRI  CRItical rate
    @property
    def cev(self): return self.xparam(3)    # CEV  Critical EVasion rate
    @property
    def mev(self): return self.xparam(4)    # MEV  Magic EVasion rate
    @property
    def mrf(self): return self.xparam(5)    # MRF  Magic ReFlection rate
    @property
    def cnt(self): return self.xparam(6)    # CNT  CouNTer attack rate
    @property
    def hrg(self): return self.xparam(7)    # HRG  Hp ReGeneration rate
    @property
    def mrg(self): return self.xparam(8)    # MRG  Mp ReGeneration rate
    @property
    def trg(self): return self.xparam(9)    # TRG  Tp ReGeneration rate
    
    # Sp-Parameters
    @property
    def tgr(self): return self.sparam(0)    # TGR  TarGet Rate
    @property
    def grd(self): return self.sparam(1)    # GRD  GuaRD effect rate
    @property
    def rec(self): return self.sparam(2)    # REC  RECovery effect rate
    @property
    def pha(self): return self.sparam(3)    # PHA  PHArmacology
    @property
    def mcr(self): return self.sparam(4)    # MCR  Mp Cost Rate
    @property
    def tcr(self): return self.sparam(5)    # TCR  Tp Charge Rate
    @property
    def pdr(self): return self.sparam(6)    # PDR  Physical Damage Rate
    @property
    def mdr(self): return self.sparam(7)    # MDR  Magical Damage Rate
    @property
    def fdr(self): return self.sparam(8)    # FDR  Floor Damage Rate
    @property
    def exr(self): return self.sparam(9)    # EXR  EXperience Rate
    
    
    def clear_param_plus(self):
        """Clear values added to parameter."""
        self._param_plus = [0] * 8
    
    
    def clearstates(self):
        """Clear state information."""
        self.states = []
        self.state_turns = {}
        self.state_steps = {}
    
    
    def erase_state(self, state_id: int):
        """Erase states."""
        if state_id in self.states:
            self.states.remove(state_id)
        if state_id in self.state_turns:
            del self.state_turns[state_id]
        if state_id in self.state_steps:
            del self.state_steps[state_id]
    
    
    def clearbuffs(self):
        """Clear buff information."""
        self.buffs = [0] * 8
        self.buff_turns = {}
    
    
    def state(self, state_id: int) -> bool:
        """Check state."""
        return state_id in self.states
    
    
    def death_state(self) -> bool:
        """Check K.O. state."""
        return self.state(self.death_state_id())
    
    
    def death_state_id(self) -> int:
        """Get state ID of K.O."""
        return 1
    
    
    def states_objects(self) -> List[Any]:
        """Get current states as an object array."""
        # Would return state objects from $datastates in full implementation
        return []
    
    
    def state_icons(self) -> List[int]:
        """Get current states as an array of icon numbers."""
        # Would collect state icons in full implementation
        return []
    
    
    def buff_icons(self) -> List[int]:
        """Get current buffs/debuffs as an array of icon numbers."""
        icons = []
        for i, lv in enumerate(self.buffs):
            icon_index = self.buff_icon_index(lv, i)
            if icon_index != 0:
                icons.append(icon_index)
        return icons
    
    
    def buff_icon_index(self, buff_level: int, param_id: int) -> int:
        """Get icon number corresponding to buff/debuff."""
        if buff_level > 0:
            return self.ICON_BUFF_START + (buff_level - 1) * 8 + param_id
        elif buff_level < 0:
            return self.ICON_DEBUFF_START + (-buff_level - 1) * 8 + param_id
        else:
            return 0
    
    
    def feature_objects(self) -> List[Any]:
        """Get array of all objects retaining features."""
        return self.states_objects()
    
    
    def all_features(self) -> List[Any]:
        """Get array of all feature objects."""
        # Would collect features from feature objects in full implementation
        return []
    
    
    def features(self) -> List[Any]:
        """Get feature object array (feature codes limited)."""
        # Would filter features by code in full implementation
        return []
    
    
    def features_with_id(self) -> List[Any]:
        """Get feature object array (feature codes and data IDs limited)."""
        # Would filter features by code and id in full implementation
        return []
    
    
    def features_pi(self, code: int, id: int) -> float:
        """Calculate complement of feature values."""
        result = 1.0
        for ft in self.features_with_id():
            result *= ft.value
        return result
    
    
    def features_sum(self, code: int, id: int) -> float:
        """Calculate sum of feature values (specify data ID)."""
        result = 0.0
        for ft in self.features_with_id():
            result += ft.value
        return result
    
    
    def features_sum_all(self, code: int) -> float:
        """Calculate sum of feature values (data ID unspecified)."""
        result = 0.0
        for ft in self.features():
            result += ft.value
        return result
    
    
    def features_set(self, code: int) -> List[int]:
        """Calculate set sum of features."""
        result = []
        for ft in self.features():
            if ft.data_id not in result:
                result.append(ft.data_id)
        return result
    
    
    def param_base(self, param_id: int) -> int:
        """Get base value of parameter."""
        return 0
    
    
    def param_plus(self, param_id: int) -> int:
        """Get added value of parameter."""
        return self._param_plus[param_id]
    
    
    def param_min(self, param_id: int) -> int:
        """Get reduced value of parameter."""
        if param_id == 1:  # MMP
            return 0
        return 1
    
    
    def param_max(self, param_id: int) -> int:
        """Get maximum value of parameter."""
        if param_id == 0:  # MHP
            return 999999
        if param_id == 1:  # MMP
            return 9999
        return 999
    
    
    def param_rate(self, param_id: int) -> float:
        """Get rate of parameter change."""
        return self.features_pi(self.FEATURE_PARAM, param_id)
    
    
    def param_buff_rate(self, param_id: int) -> float:
        """Get rate of change due to parameter buff/debuff."""
        return self.buffs[param_id] * 0.25 + 1.0
    
    
    def param(self, param_id: int) -> int:
        """Get parameter."""
        value = self.param_base(param_id) + self.param_plus(param_id)
        value *= self.param_rate(param_id) * self.param_buff_rate(param_id)
        value = min(value, self.param_max(param_id))
        value = max(value, self.param_min(param_id))
        return int(value)
    
    
    def xparam(self, xparam_id: int) -> float:
        """Get ex-parameter."""
        return self.features_sum(self.FEATURE_XPARAM, xparam_id)
    
    
    def sparam(self, sparam_id: int) -> float:
        """Get sp-parameter."""
        return self.features_pi(self.FEATURE_SPARAM, sparam_id)
    
    
    def element_rate(self, element_id: int) -> float:
        """Get element rate."""
        return self.features_pi(self.FEATURE_ELEMENT_RATE, element_id)
    
    
    def debuff_rate(self, param_id: int) -> float:
        """Get debuff rate."""
        return self.features_pi(self.FEATURE_DEBUFF_RATE, param_id)
    
    
    def state_rate(self, state_id: int) -> float:
        """Get state rate."""
        return self.features_pi(self.FEATURE_STATE_RATE, state_id)
    
    
    def state_resist_set(self) -> List[int]:
        """Get array of states to resist."""
        return self.features_set(self.FEATURE_STATE_RESIST)
    
    
    def state_resist(self, state_id: int) -> bool:
        """Determine if state is resisted."""
        return state_id in self.state_resist_set()
    
    
    def atk_elements(self) -> List[int]:
        """Get attack element."""
        return self.features_set(self.FEATURE_ATK_ELEMENT)
    
    
    def atkstates(self) -> List[int]:
        """Get attack state."""
        return self.features_set(self.FEATURE_ATK_STATE)
    
    
    def atkstates_rate(self, state_id: int) -> float:
        """Get attack state invocation rate."""
        return self.features_sum(self.FEATURE_ATK_STATE, state_id)
    
    
    def atk_speed(self) -> float:
        """Get attack speed."""
        return self.features_sum_all(self.FEATURE_ATK_SPEED)
    
    
    def atk_times_add(self) -> int:
        """Get additional attack times."""
        return max(int(self.features_sum_all(self.FEATURE_ATK_TIMES)), 0)
    
    
    def added_skill_types(self) -> List[int]:
        """Get added skill types."""
        return self.features_set(self.FEATURE_STYPE_ADD)
    
    
    def skill_type_sealed(self, stype_id: int) -> bool:
        """Determine if skill type is disabled."""
        return stype_id in self.features_set(self.FEATURE_STYPE_SEAL)
    
    
    def added_skills(self) -> List[int]:
        """Get added skills."""
        return self.features_set(self.FEATURE_SKILL_ADD)
    
    
    def skill_sealed(self, skill_id: int) -> bool:
        """Determine if skill is disabled."""
        return skill_id in self.features_set(self.FEATURE_SKILL_SEAL)
    
    
    def equip_wtype_ok(self, wtype_id: int) -> bool:
        """Determine if weapon can be equipped."""
        return wtype_id in self.features_set(self.FEATURE_EQUIP_WTYPE)
    
    
    def equip_atype_ok(self, atype_id: int) -> bool:
        """Determine if armor can be equipped."""
        return atype_id in self.features_set(self.FEATURE_EQUIP_ATYPE)
    
    
    def equip_type_fixed(self, etype_id: int) -> bool:
        """Determine if equipment is locked."""
        return etype_id in self.features_set(self.FEATURE_EQUIP_FIX)
    
    
    def equip_type_sealed(self, etype_id: int) -> bool:
        """Determine if equipment is sealed."""
        return etype_id in self.features_set(self.FEATURE_EQUIP_SEAL)
    
    
    def slot_type(self) -> int:
        """Get slot type."""
        slot_types = self.features_set(self.FEATURE_SLOT_TYPE)
        return max(slot_types) if slot_types else 0
    
    
    def dual_wield(self) -> bool:
        """Determine if dual wield."""
        return self.slot_type() == 1
    
    
    def action_plus_set(self) -> List[float]:
        """Get array of additional action time probabilities."""
        # Would collect feature values in full implementation
        return []
    
    
    def special_flag(self, flag_id: int) -> bool:
        """Determine if special flag."""
        for ft in self.features():
            if ft.data_id == flag_id:
                return True
        return False
    
    
    def collapse_type(self) -> int:
        """Get collapse effect."""
        collapse_types = self.features_set(self.FEATURE_COLLAPSE_TYPE)
        return max(collapse_types) if collapse_types else 0
    
    
    def party_ability(self, ability_id: int) -> bool:
        """Determine party ability."""
        for ft in self.features():
            if ft.data_id == ability_id:
                return True
        return False
    
    
    def auto_battle(self) -> bool:
        """Determine if auto battle."""
        return self.special_flag(self.FLAG_ID_AUTO_BATTLE)
    
    
    def guard(self) -> bool:
        """Determine if guard."""
        return self.special_flag(self.FLAG_ID_GUARD) and self.movable()
    
    
    def substitute(self) -> bool:
        """Determine if substitute."""
        return self.special_flag(self.FLAG_ID_SUBSTITUTE) and self.movable()
    
    
    def preserve_tp(self) -> bool:
        """Determine if preserve TP."""
        return self.special_flag(self.FLAG_ID_PRESERVE_TP)
    
    
    def add_param(self, param_id: int, value: int):
        """Increase parameter."""
        self._param_plus[param_id] += value
        self.refresh()
    
    def change_hp(self, value: int, enable_death: bool):
        """Change HP (for events)."""
        if not enable_death and self._hp + value <= 0:
            self.hp = 1
        else:
            self.hp += value
    
    
    def max_tp(self) -> int:
        """Get maximum value of TP."""
        return 100
    
    
    def refresh(self):
        """Refresh."""
        for state_id in self.state_resist_set():
            self.erase_state(state_id)
        self._hp = max(0, min(self._hp, self.mhp))
        self._mp = max(0, min(self._mp, self.mmp))
        if self._hp == 0:
            self.add_state(self.death_state_id())
        else:
            self.remove_state(self.death_state_id())
    
    
    def recover_all(self):
        """Recover all."""
        self.clearstates()
        self._hp = self.mhp
        self._mp = self.mmp
    
    
    def hp_rate(self) -> float:
        """Get percentage of HP."""
        return float(self._hp) / self.mhp if self.mhp > 0 else 0
    
    
    def mp_rate(self) -> float:
        """Get percentage of MP."""
        return float(self._mp) / self.mmp if self.mmp > 0 else 0
    
    
    def tp_rate(self) -> float:
        """Get percentage of TP."""
        return float(self._tp) / 100
    
    
    def hide(self):
        """Hide."""
        self._hidden = True
    
    
    def appear(self):
        """Appear."""
        self._hidden = False
    
    
    def hidden(self) -> bool:
        """Get hide state."""
        return self._hidden
    
    
    def exist(self) -> bool:
        """Determine existence."""
        return not self.hidden()
    
    
    def dead(self) -> bool:
        """Determine incapacitation."""
        return self.exist() and self.death_state()
    
    
    def alive(self) -> bool:
        """Determine survival."""
        return self.exist() and not self.death_state()
    
    
    def normal(self) -> bool:
        """Determine normality."""
        return self.exist() and self.restriction() == 0
    
    
    def inputable(self) -> bool:
        """Determine if command is inputable."""
        return self.normal() and not self.auto_battle()
    
    
    def movable(self) -> bool:
        """Determine if action is possible."""
        return self.exist() and self.restriction() < 4
    
    
    def confusion(self) -> bool:
        """Determine if character is confused."""
        return self.exist() and 1 <= self.restriction() <= 3
    
    
    def confusion_level(self) -> int:
        """Get confusion level."""
        return self.restriction() if self.confusion() else 0
    
    
    def actor(self) -> bool:
        """Determine if actor or not."""
        return False
    
    
    def enemy(self) -> bool:
        """Determine if enemy."""
        return False
    
    def sortstates(self):
        """Sorting states."""
        # Would sort states by priority in full implementation
        pass
    
    def restriction(self) -> int:
        """Get restriction."""
        restrictions = [0]
        for state in self.states_objects():
            restrictions.append(state.restriction)
        return max(restrictions)
    
    
    def most_important_state_text(self) -> str:
        """Get most important state continuation message."""
        # Would return state message in full implementation
        return ""
    
    
    def skill_wtype_ok(self, skill) -> bool:
        """Determine if skill-required weapon is equipped."""
        return True
    
    
    def skill_mp_cost(self, skill) -> int:
        """Calculate skill's MP cost."""
        return int(skill.mp_cost * self.mcr)
    
    
    def skill_tp_cost(self, skill) -> int:
        """Calculate skill's TP cost."""
        return skill.tp_cost
    
    
    def skill_cost_payable(self, skill) -> bool:
        """Determine if cost of using skill can be paid."""
        return self.tp >= self.skill_tp_cost(skill) and self.mp >= self.skill_mp_cost(skill)
    
    
    def pay_skill_cost(self, skill):
        """Pay cost of using skill."""
        self.mp -= self.skill_mp_cost(skill)
        self.tp -= self.skill_tp_cost(skill)
    
    
    def occasion_ok(self) -> bool:
        """Check when skill/item can be used."""
        # Would check battle/menu conditions in full implementation
        return True
    
    
    def usable_item_conditions_met(self, item) -> bool:
        """Check common usability conditions for skill/item."""
        return self.movable() and self.occasion_ok()
    
    
    def skill_conditions_met(self, skill) -> bool:
        """Check usability conditions for skill."""
        return (self.usable_item_conditions_met(skill) and
                self.skill_wtype_ok(skill) and 
                self.skill_cost_payable(skill) and
                not self.skill_sealed(skill.id) and 
                not self.skill_type_sealed(skill.stype_id))
    
    
    def item_conditions_met(self, item) -> bool:
        """Check usability conditions for item."""
        # Would check party item availability in full implementation
        return self.usable_item_conditions_met(item)
    
    
    def usable(self) -> bool:
        """Determine skill/item usability."""
        # Would check item type in full implementation
        return False
    
    
    def equippable(self) -> bool:
        """Determine if equippable."""
        # Would check item type and equipment conditions in full implementation
        return False
    
    
    def attack_skill_id(self) -> int:
        """Get skill ID of normal attack."""
        return 1
    
    
    def guard_skill_id(self) -> int:
        """Get skill ID of guard."""
        return 2
    
    
    def attack_usable(self) -> bool:
        """Determine usability of normal attack."""
        # Would check attack skill usability in full implementation
        return True
    
    
    def guard_usable(self) -> bool:
        """Determine usability of guard."""
        # Would check guard skill usability in full implementation
        return True

    # Additional methods that were in the original but not in your Python base
    def add_state(self, state_id: int):
        """Add state - placeholder for subclasses."""
        if state_id not in self.states:
            self.states.append(state_id)
    
    def remove_state(self, state_id: int):
        """Remove state - placeholder for subclasses."""
        if state_id in self.states:
            self.states.remove(state_id)

    def is_actor(self):
        return False

    def is_enemy(self):
        return False



class GameBattler(GameBattlerBase):
    """
    Inherits from BattlerBase and adds logic for actions, battle effects,
    and turn handling.
    """
    
    # Constants (Effects)
    EFFECT_RECOVER_HP = 11              # HP Recovery
    EFFECT_RECOVER_MP = 12              # MP Recovery
    EFFECT_GAIN_TP = 13                 # TP Gain
    EFFECT_ADD_STATE = 21               # Add State
    EFFECT_REMOVE_STATE = 22            # Remove State
    EFFECT_ADD_BUFF = 31                # Add Buff
    EFFECT_ADD_DEBUFF = 32              # Add Debuff
    EFFECT_REMOVE_BUFF = 33             # Remove Buff
    EFFECT_REMOVE_DEBUFF = 34           # Remove Debuff
    EFFECT_SPECIAL = 41                 # Special Effect
    EFFECT_GROW = 42                    # Raise Parameter
    EFFECT_LEARN_SKILL = 43             # Learn Skill
    EFFECT_COMMON_EVENT = 44            # Common Events
    
    # Constants (Special Effects)
    SPECIAL_EFFECT_ESCAPE = 0           # Escape

    def __init__(self):
        super(GameBattler, self).__init__()
        
        # Public Instance Variables
        self.battler_name = ""              # battle graphic filename
        self.battler_hue = 0                # battle graphic hue
        self.actions = []                   # combat actions (action side)
        self.speed = 0                      # action speed
        self.result = GameActionResult(self)  # action result (target side)
        self.last_target_index = 0          # last target
        self.animation_id = 0               # animation ID
        self.animation_mirror = False       # animation flip horizontal flag
        self.sprite_effect_type = None      # sprite effect
        self.magic_reflection = False       # reflection flag
        self.guarding = False
        
        GameBattler.clear_sprite_effects(self)
    
    def clear_sprite_effects(self):
        """Clear sprite effects."""
        self.animation_id = 0
        self.animation_mirror = False
        self.sprite_effect_type = None
    
    def clear_actions(self):
        """Clear actions."""
        self.actions.clear()
    
    def clearstates(self):
        """Clear state information."""
        super().clearstates()
        self.result.clear_status_effects()
    
    def add_state(self, state_id: int):
        """Add state."""
        if self.state_addable(state_id):
            if not self.state(state_id):
                self.add_new_state(state_id)
            self.reset_state_counts(state_id)
            if state_id not in self.result.added_states:
                self.result.added_states.append(state_id)
    
    def state_addable(self, state_id: int) -> bool:
        """Determine if states are addable."""
        return (self.alive() and 
                JRPG.is_data_state(state_id) and 
                not self.state_resist(state_id) and
                not self.state_removed(state_id) and 
                not self.state_restrict(state_id))
    
    def state_removed(self, state_id: int) -> bool:
        """Determine states removed during same action."""
        return state_id in self.result.removed_states
    
    def state_restrict(self, state_id: int) -> bool:
        """Determine states removed by action restriction."""
        if JRPG.data:    
            state = JRPG.data.states.get(state_id)
            if state:
                return state.get("remove_by_restriction", False) and self.restriction() > 0
        return False
    
    def add_new_state(self, state_id: int):
        """Add new state."""
        if state_id == self.death_state_id():
            self.die()
        
        if state_id not in self.states:
            self.states.append(state_id)
        
        if self.restriction() > 0:
            self.on_restrict()
        
        self.sortstates()
        self.refresh()
    
    def on_restrict(self):
        """Processing performed when action restriction occurs."""
        self.clear_actions()
        for state in self.states_objects():
            if state.state.get("remove_by_restriction", False):
                self.remove_state(state.id)
    
    def reset_state_counts(self, state_id: int):
        """Reset state counts (turns and steps)."""
        if JRPG.data:    
            state = JRPG.data.states.get(state_id)
            if state:
                max_turns = state.get("max_turns", 1)
                min_turns = state.get("min_turns", 1)

                variance = 1 + max(max_turns - min_turns, 0)
                self.state_turns[state_id] = min_turns + random.randint(0, variance - 1) if variance > 0 else min_turns
                self.state_steps[state_id] = state.get("steps_to_remove", 0)
    
    def remove_state(self, state_id: int):
        """Remove state."""
        if self.state(state_id):
            if state_id == self.death_state_id():
                self.revive()
            
            self.erase_state(state_id)
            self.refresh()
            
            if state_id not in self.result.removed_states:
                self.result.removed_states.append(state_id)
    
    def die(self):
        """Knock out."""
        self._hp = 0
        self.clearstates()
        self.clearbuffs()

    def revive(self):
        """Revive from knock out."""
        if self.hp == 0:
            self.hp = 1
    
    def escape(self):
        """Escape."""
        if hasattr(self, 'hide') and (JRPG.objects and JRPG.objects.party is not None and JRPG.objects.party.in_battle):
            self.hide()
        self.clear_actions()
        self.clearstates()
        # Sound.play_escape()  # Would be implemented in full version
    
    def add_buff(self, param_id: int, turns: int):
        """Add buff."""
        if not self.alive():
            return
        
        if not self.buff_max(param_id):
            self.buffs[param_id] += 1
        
        if self.debuff(param_id):
            self.erase_buff(param_id)
        
        self.overwritebuff_turns(param_id, turns)
        
        if param_id not in self.result.added_buffs:
            self.result.added_buffs.append(param_id)
        
        self.refresh()
    
    def add_debuff(self, param_id: int, turns: int):
        """Add debuff."""
        if not self.alive():
            return
        
        if not self.debuff_max(param_id):
            self.buffs[param_id] -= 1
        
        if self.buff(param_id):
            self.erase_buff(param_id)
        
        self.overwritebuff_turns(param_id, turns)
        
        if param_id not in self.result.added_debuffs:
            self.result.added_debuffs.append(param_id)
        
        self.refresh()
    
    def remove_buff(self, param_id: int):
        """Remove buff/debuff."""
        if not self.alive():
            return
        
        if self.buffs[param_id] == 0:
            return
        
        self.erase_buff(param_id)
        if param_id in self.buff_turns:
            del self.buff_turns[param_id]
        
        if param_id not in self.result.removed_buffs:
            self.result.removed_buffs.append(param_id)
        
        self.refresh()

    def erase_buff(self, param_id: int):
        """Erase buff/debuff."""
        self.buffs[param_id] = 0
        self.buff_turns[param_id] = 0
    
    def buff(self, param_id: int) -> bool:
        """Determine buff status."""
        return self.buffs[param_id] > 0
    
    def debuff(self, param_id: int) -> bool:
        """Determine debuff status."""
        return self.buffs[param_id] < 0
    
    def buff_max(self, param_id: int) -> bool:
        """Determine if buff is at maximum level."""
        return self.buffs[param_id] == 2
    
    def debuff_max(self, param_id: int) -> bool:
        """Determine if debuff is at maximum level."""
        return self.buffs[param_id] == -2
    
    def overwritebuff_turns(self, param_id: int, turns: int):
        """Overwrite buff/debuff turns."""
        current_turns = self.buff_turns.get(param_id, 0)
        if current_turns < turns:
            self.buff_turns[param_id] = turns

    def updatestate_turns(self):
        """Update state turn count."""
        for state in self.states_objects():
            if self.state_turns.get(state.id, 0) > 0:
                self.state_turns[state.id] -= 1
    
    def updatebuff_turns(self):
        """Update buff/debuff turn count."""
        for param_id in list(self.buff_turns.keys()):
            if self.buff_turns[param_id] > 0:
                self.buff_turns[param_id] -= 1
    
    def remove_battlestates(self):
        """Remove battle states."""
        for state in self.states_objects():
            if state.remove_at_battle_end:
                self.remove_state(state.id)
    
    def remove_allbuffs(self):
        """Remove all buffs/debuffs."""
        for param_id in range(len(self.buffs)):
            self.remove_buff(param_id)
    
    def removestates_auto(self, timing: int):
        """Automatically remove states."""
        for state in self.states_objects():
            state_turns = self.state_turns.get(state.id, 0)
            if state_turns == 0 and state.auto_removal_timing == timing:
                self.remove_state(state.id)
    
    def removebuffs_auto(self):
        """Automatically remove buffs/debuffs."""
        for param_id in range(len(self.buffs)):
            if self.buffs[param_id] != 0 and self.buff_turns.get(param_id, 0) <= 0:
                self.remove_buff(param_id)
    
    def removestates_by_damage(self):
        """Remove state by damage."""
        for state in self.states_objects():
            if (state.remove_by_damage and 
                random.randint(0, 99) < state.chance_by_damage):
                self.remove_state(state.id)
    
    def make_action_times(self) -> int:
        """Determine action times."""
        result = 1
        for p in self.action_plus_set():
            if random.random() < p:
                result += 1
        return result
    
    def make_actions(self):
        """Create battle action."""
        self.clear_actions()
        if not self.movable():
            return
        times = self.make_action_times()
        self.actions = [GameAction(self) for _ in range(times)]
    
    def make_speed(self):
        """Determine action speed."""
        if self.actions:
            speeds = [action.speed for action in self.actions]
            self.speed = min(speeds) if speeds else 0
        else:
            self.speed = 0
    
    def current_action(self):
        """Get current action."""
        return self.actions[0] if self.actions else None
    
    def remove_current_action(self):
        """Remove current action."""
        if self.actions:
            self.actions.pop(0)
    
    def force_action(self, skill_id: int, target_index: int):
        """Force action."""
        self.clear_actions()
        action = GameAction(self)
        action.set_skill(skill_id)
        
        if target_index == -2:
            action.target_index = self.last_target_index
        elif target_index == -1:
            action.decide_random_target()
        else:
            action.target_index = target_index
        
        self.actions.append(action)
    
    def make_damage_value(self, user, item):
        """Calculate damage."""
        value = item.damage.eval(user, self, self.game_variables)
        value *= self.item_element_rate(user, item)
        if item.physical:
            value *= self.pdr
        if item.magical:
            value *= self.mdr
        if item.damage.recover:
            value *= self.rec
        if self.result.critical:
            value = self.apply_critical(value)
        value = self.apply_variance(value, item.damage.variance)
        value = self.apply_guard(value)
        self.result.make_damage(int(value), item)
    
    def item_element_rate(self, user, item) -> float:
        """Get element modifier for skill/item."""
        if item.damage.element_id < 0:
            if not user.atk_elements:
                return 1.0
            return self.elements_max_rate(user.atk_elements)
        else:
            return self.element_rate(item.damage.element_id)
    
    def elements_max_rate(self, elements: List[int]) -> float:
        """Get maximum elemental adjustment amount."""
        rates = [0.0]
        for i in elements:
            rates.append(self.element_rate(i))
        return max(rates)
    
    def apply_critical(self, damage: float) -> float:
        """Apply critical."""
        return damage * 3
    
    def apply_variance(self, damage: float, variance: int) -> float:
        """Applying variance."""
        amp = max(int(abs(damage) * variance / 100), 0)
        var = random.randint(0, amp) + random.randint(0, amp) - amp
        return damage + var if damage >= 0 else damage - var
    
    def apply_guard(self, damage: float) -> float:
        """Applying guard adjustment."""
        if damage > 0 and self.guard():
            return damage / (2 * self.grd)
        return damage
    
    def execute_damage(self, user):
        """Damage processing."""
        if self.result.hp_damage > 0:
            self.on_damage(self.result.hp_damage)
        
        self.hp -= self.result.hp_damage
        self.mp -= self.result.mp_damage
        user.hp += self.result.hp_drain
        user.mp += self.result.mp_drain
    
    def use_item(self, item):
        """Use skill/item."""
        # if isinstance(item, RPGSkill): # TODO
        #     self.pay_skill_cost(item)
        # if isinstance(item, RPGItem): # TODO
        #     self.consume_item(item)
        
        for effect in item.effects:
            self.item_global_effect_apply(effect)
    
    def consume_item(self, item):
        """Consume items."""
        if JRPG.objects and JRPG.objects.party:
            JRPG.objects.party.consume_item(item)
    
    def item_global_effect_apply(self, effect):
        """Apply effect of use to other than user."""
        if effect.code == self.EFFECT_COMMON_EVENT:
            # self.game_temp.reserve_common_event(effect.data_id)  # Would be implemented
            pass
    
    def item_test(self, user, item) -> bool:
        """Test skill/item application."""
        if item.for_dead_friend != self.dead():
            return False
        
        if JRPG.objects and JRPG.objects.party and JRPG.objects.party.in_battle:
            return True
        if item.for_opponent:
            return True
        if item.damage.recover:
            if item.damage.to_hp and self.hp < self.mhp:
                return True
            if item.damage.to_mp and self.mp < self.mmp:
                return True
        return self.item_has_any_valid_effects(user, item)

    def item_has_any_valid_effects(self, user, item) -> bool:
        """Determine if skill/item has any valid effects."""
        for effect in item.effects:
            if self.item_effect_test(user, item, effect):
                return True
        return False
    
    def item_cnt(self, user, item) -> float:
        """Calculate counterattack rate for skill/item."""
        if not item.physical:  # Hit type is not physical
            return 0.0
        if not self.opposite(user):  # No counterattack on allies
            return 0.0
        return self.cnt  # Return counterattack rate

    def item_mrf(self, item) -> float:
        """Calculate reflection rate of skill/item."""
        if item.magical:  # Return magic reflection if magic attack
            return self.mrf
        return 0.0
    
    def item_hit(self, user, item) -> float:
        """Calculate hit rate of skill/item."""
        rate = item.success_rate * 0.01  # Get success rate
        if item.physical:  # Physical attack: Multiply hit rate
            rate *= user.hit
        return rate  # Return calculated hit rate

    def item_eva(self, item) -> float:
        """Calculate evasion rate for skill/item."""
        if item.physical:  # Return evasion if physical attack
            return self.eva
        if item.magical:  # Return magic evasion if magic attack
            return self.mev
        return 0.0

    def item_cri(self, user, item) -> float:
        """Calculate critical rate of skill/item."""
        if item.damage.critical:
            return user.cri * (1 - self.cev)
        return 0.0
    
    def attack_apply(self, attacker):
        """Apply normal attack effects."""
        # self.item_apply(attacker, self.data_skills[attacker.attack_skill_id])
        pass  # Would be implemented with full data structures
    
    def item_apply(self, user, item):
        """Apply effect of skill/item."""
        self.result.clear()
        self.result.used = self.item_test(user, item)
        self.result.missed = (self.result.used and random.random() >= self.item_hit(user, item))
        self.result.evaded = (not self.result.missed and random.random() < self.item_eva(item))
        
        if self.result.hit:
            if not item.damage.none:
                self.result.critical = (random.random() < self.item_cri(user, item))
                self.make_damage_value(user, item)
                self.execute_damage(user)
            
            for effect in item.effects:
                self.item_effect_apply(user, item, effect)
            
            self.item_user_effect(user, item)

    def item_effect_test(self, user, item, effect) -> bool:
        """Test effect."""
        if effect.code == self.EFFECT_RECOVER_HP:
            return (self.hp < self.mhp or effect.value1 < 0 or effect.value2 < 0)
        elif effect.code == self.EFFECT_RECOVER_MP:
            return (self.mp < self.mmp or effect.value1 < 0 or effect.value2 < 0)
        elif effect.code == self.EFFECT_ADD_STATE:
            return not self.state(effect.data_id)
        elif effect.code == self.EFFECT_REMOVE_STATE:
            return self.state(effect.data_id)
        elif effect.code == self.EFFECT_ADD_BUFF:
            return not self.buff_max(effect.data_id)
        elif effect.code == self.EFFECT_ADD_DEBUFF:
            return not self.debuff_max(effect.data_id)
        elif effect.code == self.EFFECT_REMOVE_BUFF:
            return self.buff(effect.data_id)
        elif effect.code == self.EFFECT_REMOVE_DEBUFF:
            return self.debuff(effect.data_id)
        elif effect.code == self.EFFECT_LEARN_SKILL:
            if self.actor():
                if JRPG.data and JRPG.data.skills:
                    skill_ref = JRPG.data.skills.get(effect.data_id)
                else:
                    skill_ref = None

                try:
                    return self.actor() and self.skills and not self.skills.include(skill_ref) # type: ignore
                except:
                    pass
            
            return False
        else:
            return True
    
    def item_effect_apply(self, user, item, effect):
        """Apply effect."""
        method_table = {
            self.EFFECT_RECOVER_HP: self.item_effect_recover_hp,
            self.EFFECT_RECOVER_MP: self.item_effect_recover_mp,
            self.EFFECT_GAIN_TP: self.item_effect_gain_tp,
            self.EFFECT_ADD_STATE: self.item_effect_add_state,
            self.EFFECT_REMOVE_STATE: self.item_effect_remove_state,
            self.EFFECT_ADD_BUFF: self.item_effect_add_buff,
            self.EFFECT_ADD_DEBUFF: self.item_effect_add_debuff,
            self.EFFECT_REMOVE_BUFF: self.item_effect_remove_buff,
            self.EFFECT_REMOVE_DEBUFF: self.item_effect_remove_debuff,
            self.EFFECT_SPECIAL: self.item_effect_special,
            self.EFFECT_GROW: self.item_effect_grow,
            self.EFFECT_LEARN_SKILL: self.item_effect_learn_skill,
            self.EFFECT_COMMON_EVENT: self.item_effect_common_event,
        }
        
        method = method_table.get(effect.code)
        if method:
            method(user, item, effect)
    
    def item_effect_recover_hp(self, user, item, effect):
        """[HP Recovery] effect."""
        value = (self.mhp * effect.value1 + effect.value2) * self.rec
        if effect.type == "RPG_Item":
            value *= user.pha
        # if isinstance(item, RPG_Item):
        #     value *= user.pha
        value = int(value)
        self.result.hp_damage -= value
        self.result.success = True
        self.hp += value
    
    def item_effect_recover_mp(self, user, item, effect):
        """[MP Recovery] effect."""
        value = (self.mmp * effect.value1 + effect.value2) * self.rec
        if effect.type == "RPG_Item":
            value *= user.pha
        # if isinstance(item, RPG_Item):
        #     value *= user.pha
        value = int(value)
        self.result.mp_damage -= value
        self.result.success = (value != 0)
        self.mp += value
    
    def item_effect_gain_tp(self, user, item, effect):
        """[TP Gain] effect."""
        value = int(effect.value1)
        self.result.tp_damage -= value
        self.result.success = (value != 0)
        self.tp += value
    
    def item_effect_add_state(self, user, item, effect):
        """[Add State] effect."""
        if effect.data_id == 0:
            self.item_effect_add_state_attack(user, item, effect)
        else:
            self.item_effect_add_state_normal(user, item, effect)
    
    def item_effect_add_state_attack(self, user, item, effect):
        """[Add State] effect: Normal attack."""
        for state_id in user.atkstates:
            chance = effect.value1
            chance *= self.state_rate(state_id)
            chance *= user.atkstates_rate(state_id)
            chance *= self.luk_effect_rate(user)
            if random.random() < chance:
                self.add_state(state_id)
                self.result.success = True
    
    def item_effect_add_state_normal(self, user, item, effect):
        """[Add State] effect: Normal."""
        chance = effect.value1
        if self.opposite(user):
            chance *= self.state_rate(effect.data_id)
            chance *= self.luk_effect_rate(user)
        if random.random() < chance:
            self.add_state(effect.data_id)
            self.result.success = True
    
    def item_effect_remove_state(self, user, item, effect):
        """[Remove State] effect."""
        chance = effect.value1
        if random.random() < chance:
            self.remove_state(effect.data_id)
            self.result.success = True
    
    def item_effect_add_buff(self, user, item, effect):
        """[Buff] effect."""
        self.add_buff(effect.data_id, effect.value1)
        self.result.success = True
    
    def item_effect_add_debuff(self, user, item, effect):
        """[Debuff] effect."""
        chance = self.debuff_rate(effect.data_id) * self.luk_effect_rate(user)
        if random.random() < chance:
            self.add_debuff(effect.data_id, effect.value1)
            self.result.success = True
    
    def item_effect_remove_buff(self, user, item, effect):
        """[Remove Buff] effect."""
        if self.buffs[effect.data_id] > 0:
            self.remove_buff(effect.data_id)
        self.result.success = True
    
    def item_effect_remove_debuff(self, user, item, effect):
        """[Remove Debuff] effect."""
        if self.buffs[effect.data_id] < 0:
            self.remove_buff(effect.data_id)
        self.result.success = True
    
    def item_effect_special(self, user, item, effect):
        """[Special Effect] effect."""
        if effect.data_id == self.SPECIAL_EFFECT_ESCAPE:
            self.escape()
        self.result.success = True
    
    def item_effect_grow(self, user, item, effect):
        """[Raise Parameter] effect."""
        self.add_param(effect.data_id, int(effect.value1))
        self.result.success = True
    
    def learn_skill(self, skill_id: int):
        """Learn skill."""
        pass
    
    def item_effect_learn_skill(self, user, item, effect):
        """[Learn Skill] effect."""
        if self.actor():
            self.learn_skill(effect.data_id)
        self.result.success = True
    
    def item_effect_common_event(self, user, item, effect):
        """[Common Event] effect."""
        pass
    
    def item_user_effect(self, user, item):
        """Effect of skill/item on using side."""
        user.tp += item.tp_gain * user.tcr
    
    def luk_effect_rate(self, user) -> float:
        """Get effect change rate by luck."""
        return max(1.0 + (user.luk - self.luk) * 0.001, 0.0)
    
    def opposite(self, battler) -> bool:
        """Determine if hostile relation."""
        return self.actor() != battler.actor() or battler.magic_reflection
    
    def perform_map_damage_effect(self):
        """Effect when taking damage on map."""
        pass
    
    def init_tp(self):
        """Initialize TP."""
        self.tp = random.random() * 25
    
    def clear_tp(self):
        """Clear TP."""
        self.tp = 0
    
    def charge_tp_by_damage(self, damage_rate: float):
        """Charge TP by damage suffered."""
        self.tp += 50 * damage_rate * self.tcr
    
    def regenerate_hp(self):
        """Regenerate HP."""
        damage = -int(self.mhp * self.hrg)
        if JRPG.objects and JRPG.objects.party and JRPG.objects.party.in_battle and damage > 0:
            self.perform_map_damage_effect()
        self.result.hp_damage = min(damage, self.max_slip_damage())
        self.hp -= self.result.hp_damage
    
    def max_slip_damage(self) -> int:
        """Get maximum value of slip damage."""
        # Would check system options in full implementation
        return max(self.hp - 1, 0)
    
    def regenerate_mp(self):
        """Regenerate MP."""
        self.result.mp_damage = -int(self.mmp * self.mrg)
        self.mp -= self.result.mp_damage
    
    def regenerate_tp(self):
        """Regenerate TP."""
        self.tp += 100 * self.trg
    
    def regenerate_all(self):
        """Regenerate all."""
        if self.alive():
            self.regenerate_hp()
            self.regenerate_mp()
            self.regenerate_tp()
    
    def on_battle_start(self):
        """Processing at start of battle."""
        if not self.preserve_tp():
            self.init_tp()
    
    def on_action_end(self):
        """Processing at end of action."""
        self.result.clear()
        self.removestates_auto(1)
        self.removebuffs_auto()
    
    def on_turn_end(self):
        """Processing at end of turn."""
        self.result.clear()
        self.regenerate_all()
        self.updatestate_turns()
        self.updatebuff_turns()
        self.removestates_auto(2)
    
    def on_battle_end(self):
        """Processing at end of battle."""
        self.result.clear()
        self.remove_battlestates()
        self.remove_allbuffs()
        self.clear_actions()
        if not self.preserve_tp():
            self.clear_tp()
        self.appear()
    
    def on_damage(self, value: int):
        """Processing when suffering damage."""
        self.removestates_by_damage()
        self.charge_tp_by_damage(float(value) / self.mhp)

    


class GameActor(GameBattler):
    """
    Handles actor data. It is used within GameActors and GameParty.
    This class is data-driven, initialized from a dictionary.
    """
    def __init__(self, actor_id: int, actor_data: Dict[str, Any]):
        super(GameActor, self).__init__()
        self._actor_id = actor_id
        self.actor_data = actor_data # TODO: get rid of that and recreate it when needed
        self.name: str = actor_data.get("name", "Actor")
        self.nickname: str = actor_data.get("nickname", "")
        self.class_id: int = actor_data.get("class_id", 1)
        self.level: int = actor_data.get("initial_level", 1)
        self.exp = {}
        self.equips: List[int] = actor_data.get("equips", [0,0,0,0,0])
        self.skills = []
        self.action_input_index = 0
        self.last_skill = GameBaseItem()

        # Graphics
        self.character_name: str = actor_data.get("character_name", "")
        self.character_index: int = actor_data.get("character_index", 0)
        self.face_name: str = actor_data.get("face_name", "")
        self.face_index: int = actor_data.get("face_index", 0)
        
        # Misc
        self._description: List[str] = actor_data.get("description", ["A mysterious hero."])
        self.params: List[int] = actor_data.get("params", [0,0,0,0,0,0,0,0]) # TODO: params are from classes !
        self.note: str = actor_data.get("note", "")

        GameActor.setup(self, actor_id)
    
    def setup(self, actor_id: int):
        """Setup actor with given ID."""
        self._actor_id = actor_id
        self.name = self.actor.get("name", "Actor")
        self.nickname = self.actor.get("nickname", "")
        
        self.init_graphics()
        
        self.class_id = self.actor.get("class_id", 1)
        self.level = self.actor.get("initial_level", 1)
        self.exp = {}
        self.equips = []
        
        self.init_exp()
        self.init_skills()
        # init_equips would go here if we had equipment data
        self.clear_param_plus()

        # Base Parameters
        
        # Current stats
        self.recover_all()

    @property
    def actor(self) -> Dict[str, Any]:
        """Get actor object from data."""
        # Later we should re-create the actor on the fly. It may be useful for serializing
        return self.actor_data
    
    def init_graphics(self):
        """Initialize graphics from actor data."""
        self.character_name = self.actor.get("character_name", "")
        self.character_index = self.actor.get("character_index", 0)
        self.face_name = self.actor.get("face_name", "")
        self.face_index = self.actor.get("face_index", 0)
    
    def exp_for_level(self, level: int) -> int:
        """Get total EXP required for rising to specified level."""
        # TODO: Simplified implementation - in a full version this would use class data
        return level * 100  # Placeholder calculation
    def init_exp(self):
        """Initialize EXP."""
        self.exp[self.class_id] = self.current_level_exp()
    
    def current_level_exp(self) -> int:
        """Get minimum EXP for current level."""
        return self.exp_for_level(self.level)

    def next_level_exp(self) -> int:
        """Get EXP for next level."""
        return self.exp_for_level(self.level + 1)

    def max_level(self) -> int:
        """Maximum level."""
        return self.actor.get("max_level", 99)

    def max_level_p(self) -> bool:
        """Determine maximum level."""
        return self.level >= self.max_level()

    def init_skills(self):
        """Initialize skills."""
        self.skills = []
        # In a full implementation, this would iterate through class learnings
        # and learn skills based on current level

    def init_equips(self, equips: List[int]):
        """Initialize equipment."""
        # This would be implemented with proper equipment handling
        pass

    def index_to_etype_id(self, index: int) -> int:
        """Convert index set by editor to equipment type ID."""
        # Simplified - would check for dual wield in full implementation
        return index

    def slot_list(self, etype_id: int) -> List[int]:
        """Convert from equipment type to list of slot IDs."""
        # Simplified implementation
        equip_slots = self.equip_slots()
        result = []
        for i, e in enumerate(equip_slots):
            if e == etype_id:
                result.append(i)
        return result

    def empty_slot(self, etype_id: int) -> Optional[int]:
        """Convert from equipment type to slot ID (empty take precedence)."""
        # Simplified implementation
        return 0  # Placeholder

    def equip_slots(self) -> List[int]:
        """Get equipment slot array."""
        # Simplified - would check for dual wield in full implementation
        return [0, 1, 2, 3, 4]

    def weapons(self) -> List[Any]:
        """Get weapon object array."""
        # Would return equipped weapons in full implementation
        return []

    def armors(self) -> List[Any]:
        """Get armor object array."""
        # Would return equipped armors in full implementation
        return []

    def equips_objects(self) -> List[Any]:
        """Get equipped item object array."""
        # Would return all equipped items in full implementation
        return []

    def equip_change_ok(self, slot_id: int) -> bool:
        """Determine if equipment change possible."""
        # Simplified implementation
        return True

    def change_equip(self, slot_id: int, item: Any):
        """Change equipment."""
        # Implementation would go here
        pass

    def force_change_equip(self, slot_id: int, item: Any):
        """Forcibly change equipment."""
        # Implementation would go here
        pass

    def trade_item_with_party(self, new_item: Any, old_item: Any) -> bool:
        """Trade item with party."""
        # Implementation would go here
        return True

    def change_equip_by_id(self, slot_id: int, item_id: int):
        """Change equipment (specify with ID)."""
        # Implementation would go here
        pass

    def discard_equip(self, item: Any):
        """Discard equipment."""
        # Implementation would go here
        pass

    def release_unequippable_items(self, item_gain: bool = True):
        """Remove equipment that cannot be equipped."""
        # Implementation would go here
        pass

    def clear_equipments(self):
        """Remove all equipment."""
        # Implementation would go here
        pass

    def optimize_equipments(self):
        """Ultimate equipment."""
        # Implementation would go here
        pass

    def skill_wtype_ok(self, skill: Any) -> bool:
        """Determine if skill-required weapon is equipped."""
        # Implementation would go here
        return True

    def wtype_equipped(self, wtype_id: int) -> bool:
        """Determine if specific type of weapon is equipped."""
        # Implementation would go here
        return False

    def refresh(self):
        """Refresh."""
        self.release_unequippable_items()
        super().refresh()

    def is_actor(self) -> bool:
        """Determine if actor or not."""
        return True

    def friends_unit(self):
        """Get allied units."""
        # Would return $game_party in full implementation
        return None

    def opponents_unit(self):
        """Get enemy units."""
        # Would return $game_troop in full implementation
        return None

    def id(self) -> int:
        """Get actor ID."""
        return self._actor_id

    def index(self) -> Optional[int]:
        """Get index."""
        # Would find self in party members in full implementation
        return 0

    def battle_member(self) -> bool:
        """Determine battle members."""
        # Would check if in battle members in full implementation
        return True

    def class_object(self):
        """Get class object."""
        # Would return $data_classes[self.class_id] in full implementation
        return None

    def get_skills(self) -> List[Any]:
        """Get skill object array."""
        # Would return skill objects in full implementation
        return []

    def usable_skills(self) -> List[Any]:
        """Get array of currently usable skills."""
        # Would filter usable skills in full implementation
        return []

    def feature_objects(self) -> List[Any]:
        """Get array of all objects retaining features."""
        # Would combine various feature objects in full implementation
        return []

    def atk_elements(self) -> List[int]:
        """Get attack element."""
        # Would calculate attack elements in full implementation
        return [1]  # Physical element

    def param_max(self, param_id: int) -> int:
        """Get maximum value of parameter."""
        if param_id == 0:  # MHP
            return 9999
        return super().param_max(param_id)
    
    def param_base(self, param_id: int) -> int:
        """Get base value of parameter."""
        # Simplified implementation - would use class params in full version
        params = self.params
        if param_id < len(params):
            return params[param_id]
        return 0

    def param_plus(self, param_id: int) -> int:
        """Get added value of parameter."""
        # Would calculate from equipment in full implementation
        return super().param_plus(param_id)

    def atk_animation_id1(self) -> int:
        """Get normal attack animation ID."""
        # Would determine based on weapons in full implementation
        return 1

    def atk_animation_id2(self) -> int:
        """Get animation ID of normal attack (dual wield: weapon 2)."""
        # Would determine based on weapons in full implementation
        return 0

    def change_exp(self, exp: int, show: bool):
        """Change experience."""
        self.exp[self.class_id] = max(exp, 0)
        # Level up/down logic would go here
        self.refresh()

    def gain_exp(self, exp: int):
        """Get experience."""
        # Would apply experience rate in full implementation
        self.change_exp(self.exp.get(self.class_id, 0) + exp, True)

    def change_level(self, level: int, show: bool):
        """Change level."""
        level = max(1, min(level, self.max_level()))
        self.change_exp(self.exp_for_level(level), show)

    def learn_skill(self, skill_id: int):
        """Learn skill."""
        if skill_id not in self.skills:
            self.skills.append(skill_id)
            self.skills.sort()

    def forget_skill(self, skill_id: int):
        """Forget skill."""
        if skill_id in self.skills:
            self.skills.remove(skill_id)

    def skill_learn(self, skill: Any) -> bool:
        """Determine if skill is already learned."""
        # Would check if skill is learned in full implementation
        return False

    def description(self) -> List[str]:
        """Get description."""
        return self._description or ["A mysterious hero."]

    def change_class(self, class_id: int, keep_exp: bool = False):
        """Change class."""
        if keep_exp:
            self.exp[class_id] = self.exp.get(self.class_id, 0)
        self.class_id = class_id
        self.change_exp(self.exp.get(class_id, 0), False)
        self.refresh()

    def set_graphic(self, character_name: str, character_index: int, 
                   face_name: str, face_index: int):
        """Change graphics."""
        self.character_name = character_name
        self.character_index = character_index
        self.face_name = face_name
        self.face_index = face_index

    def use_sprite(self) -> bool:
        """Use sprites?"""
        return False

    def perform_damage_effect(self):
        """Execute damage effect."""
        # Would perform visual effects in full implementation
        pass

    def perform_collapse_effect(self):
        """Execute collapse effect."""
        # Would perform visual effects in full implementation
        pass

    def make_action_list(self) -> List[Any]:
        """Create action candidate list for auto battle."""
        # Would create action list in full implementation
        return []

    def make_auto_battle_actions(self):
        """Create action during auto battle."""
        # Would set auto battle actions in full implementation
        pass

    def make_confusion_actions(self):
        """Create action during confusion."""
        # Would set confusion actions in full implementation
        pass

    def make_actions(self):
        """Create battle action."""
        super().make_actions()
        # Would handle auto battle/confusion in full implementation

    def on_player_walk(self):
        """Processing performed when player takes 1 step."""
        # Would handle walking effects in full implementation
        pass

    def updatestate_steps(self, state: Any):
        """Update step count for state."""
        # Would update state steps in full implementation
        pass

    def show_added_states(self):
        """Show added state."""
        # Would show state messages in full implementation
        pass

    def show_removed_states(self):
        """Show removed state."""
        # Would show state messages in full implementation
        pass

    def steps_for_turn(self) -> int:
        """Number of steps regarded as one turn in battle."""
        return 20

    def turn_end_on_map(self):
        """End of turn processing on map screen."""
        # Would handle turn end processing in full implementation
        pass

    def check_floor_effect(self):
        """Determine floor effect."""
        # Would check floor effects in full implementation
        pass

    def execute_floor_damage(self):
        """Floor damage processing."""
        # Would apply floor damage in full implementation
        pass

    def basic_floor_damage(self) -> int:
        """Get base value for floor damage."""
        return 10

    def max_floor_damage(self) -> int:
        """Get maximum value for floor damage."""
        # Would check system options in full implementation
        return self.hp - 1

    def perform_map_damage_effect(self):
        """Execute damage effect on map."""
        # Would perform visual effects in full implementation
        pass

    def clear_actions(self):
        """Clear actions."""
        super().clear_actions()
        self.action_input_index = 0

    def input(self):
        """Get action being input."""
        # Would return current action in full implementation
        return None

    def next_command(self) -> bool:
        """To next command input."""
        if self.action_input_index >= len(self.actions) - 1:
            return False
        self.action_input_index += 1
        return True

    def prior_command(self) -> bool:
        """To previous command input."""
        if self.action_input_index <= 0:
            return False
        self.action_input_index -= 1
        return True
    def get_info_text(self) -> List[str]:
        """Returns a formatted list of strings with the actor's info."""
        info = [self.name + ", Lvl " + str(self.level)]
        info.extend(self.description())
        return info
    
    def to_dict(self) -> Dict[str, Any]:
        """Serializes the actor's current mutable state."""
        return {
            "id": self._actor_id,
            "battlerName": self.battler_name or "",
            "characterIndex": self.character_index,
            "characterName": self.character_name or "!Crystal",
            "classId": self.class_id or 0,
            "equips": self.equips[:5],
            "faceIndex": self.face_index or 0,
            "faceName": self.face_name or "",
            "traits": [],
            "initialLevel": self.level or 1,
            "maxLevel": self.max_level or 99,
            "name": self.name or "",
            "nickname": self.nickname or "",
            "params": self.params or [0,0,0,0,0,0,0,0],
            "note": self.note or "",
            "description": self.description or [""]
        }

    def from_dict(self, data: Dict[str, Any]):
        """Applies saved state data to this actor instance."""
        # Restore basic properties
        self._actor_id = data.get("id", self._actor_id)
        self.battler_name = data.get("battlerName", self.battler_name)
        self.character_index = data.get("characterIndex", self.character_index)
        self.character_name = data.get("characterName", self.character_name)
        self.class_id = data.get("classId", self.class_id)
        self.face_index = data.get("faceIndex", self.face_index)
        self.face_name = data.get("faceName", self.face_name)
        self.name = data.get("name", self.name)
        self.nickname = data.get("nickname", self.nickname)
        self.note = data.get("note", self.note)
        self.description = data.get("description", self.description)

        # Restore equips (ensure it's a list, take up to 5)
        equips = data.get("equips", self.equips)
        if isinstance(equips, list):
            self.equips[:] = equips[:5]
        else:
            self.equips[:] = self.equips[:5]  # fallback

        # Restore parameters (ensure correct length and type)
        params = data.get("params", self.params)
        if isinstance(params, list) and len(params) == 8:
            self.params[:] = params
        else:
            self.params = [0, 0, 0, 0, 0, 0, 0, 0]

        # Level-related
        self.level = data.get("initialLevel", self.level)
        self.max_level = data.get("maxLevel", self.max_level)

        # HP and MP (must be within valid bounds)
        self._hp = data.get("hp", self._hp)
        self._mp = data.get("mp", self._mp)

        # Other runtime state
        self.talk_count = data.get("talk_count", 0)

        # Traits (currently empty)
        # traits_data = data.get("traits", [])

        self.refresh()