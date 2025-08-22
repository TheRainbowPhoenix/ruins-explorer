# cpgame/game_objects/party.py
# Manages the player's party of actors.

import random

try:
    from typing import List, Optional, Any, Dict, Union
    from cpgame.game_objects.actor import GameActor
except:
    pass

from cpgame.systems.jrpg import JRPG
from cpgame.game_objects.item import GameBaseItem

class GameUnit:
    def __init__(self) -> None:
        self._in_battles = False
    
    @property
    def in_battle(self) -> bool:
        return self.in_battle

    def members(self) -> List[Any]:
        return []
    
    def alive_members(self) -> List[Any]:
        return [member for member in self.members() if member.alive()]
    
    def dead_members(self) -> List[Any]:
        return [member for member in self.members() if member.dead()]
    
    def movable_members(self) -> List[Any]:
        return [member for member in self.members() if member.movable()]
    
    def clear_actions(self) -> None:
        for member in self.members():
            member.clear_actions()

    def agi(self) -> int:
        if len(self.members()) == 0:
            return 1
        total_agi = sum(member.agi() for member in self.members())
        return total_agi // len(self.members())
    
    def tgr_sum(self) -> float:
        return sum(member.tgr() for member in self.alive_members())
    
    def random_target(self) -> Optional[Any]:
        if not self.alive_members():
            return None
        tgr_rand = random.random() * self.tgr_sum()
        for member in self.alive_members():
            tgr_rand -= member.tgr()
            if tgr_rand < 0:
                return member
        return self.alive_members()[0] if self.alive_members() else None
    
    def random_dead_target(self) -> Optional[Any]:
        if not self.dead_members():
            return None
        return self.dead_members()[random.randint(0, len(self.dead_members()) - 1)]
    
    def smooth_target(self, index: int) -> Optional[Any]:
        members = self.members()
        if 0 <= index < len(members):
            member = members[index]
            if member and member.alive():
                return member
        alive_members = self.alive_members()
        return alive_members[0] if alive_members else None
    
    def smooth_dead_target(self, index: int) -> Optional[Any]:
        members = self.members()
        if 0 <= index < len(members):
            member = members[index]
            if member and member.dead():
                return member
        dead_members = self.dead_members()
        return dead_members[0] if dead_members else None
    
    def clear_results(self) -> List[Any]:
        result = []
        for member in self.members():
            if member.result:
                member.result.clear()
                result.append(member)
        return result
    
    def on_battle_start(self) -> None:
        for member in self.members():
            member.on_battle_start()
        self._in_battle = True

    def on_battle_end(self) -> None:
        self._in_battle = False
        for member in self.members():
            member.on_battle_end()
    
    def make_actions(self) -> None:
        for member in self.members():
            member.make_actions()
    
    def all_dead(self) -> bool:
        return len(self.alive_members()) == 0
    
    def substitute_battler(self) -> Optional[Any]:
        for member in self.members():
            if member.substitute():
                return member
        return None
    

class GameParty(GameUnit):
    """
    This class handles parties. Information such as gold and items is included.
    """

    ABILITY_ENCOUNTER_HALF    = 0           # halve encounters
    ABILITY_ENCOUNTER_NONE    = 1           # disable encounters
    ABILITY_CANCEL_SURPRISE   = 2           # disable surprise
    ABILITY_RAISE_PREEMPTIVE  = 3           # increase preemptive strike rate
    ABILITY_GOLD_DOUBLE       = 4           # double money earned
    ABILITY_DROP_ITEM_DOUBLE  = 5           # double item acquisition rate

    @property
    def gold(self) -> int:
        return self._gold
    
    @property
    def steps(self) -> int:
        return self._steps
    
    @property
    def last_item(self) -> Any:
        return self._last_item

    def __init__(self):
        super().__init__()
        self._gold = 1000
        self._items: Dict[int, int] = {}
        self._weapons: Dict[int, int] = {}
        self._armors: Dict[int, int] = {}

        self._steps = 0
        self._last_item = GameBaseItem()
        self._menu_actor_id = 0
        self._target_actor_id = 0
        self._actors: List[int] = []
        self.init_all_items()

    def init_all_items(self) -> None:
        self._items = {}
        self._weapons = {}
        self._armors = {}

    def exists(self) -> bool:
        return len(self._actors) > 0 if self._actors else False

    def members(self) -> List[Any]:
        return self.battle_members() if self.in_battle else self.all_members()

    def all_members(self) -> List['GameActor']:
        if self._actors and JRPG.objects and JRPG.objects.actors:
            return [JRPG.objects.actors[id] for id in self._actors] # type: ignore
        else:
            return []

    def battle_members(self) -> List['GameActor']:
        return [actor for actor in self.all_members()[0:self.max_battle_members()] if actor.exist()]

    def max_battle_members(self) -> int:
        return 4

    def leader(self) -> Optional['GameActor']:
        battle_members = self.battle_members()
        return battle_members[0] if battle_members else None

    def items(self) -> List[Any]:
        if JRPG.data and JRPG.data.items:
            return [JRPG.data.items.get(id) for id in sorted(self._items.keys())]
        else:
            return []

    def weapons(self) -> List[Any]:
        if JRPG.data and JRPG.data.weapons:
            return [JRPG.data.weapons.get(id) for id in sorted(self._weapons.keys())]
        else:
            return []

    def armors(self) -> List[Any]:
        if JRPG.data and JRPG.data.armors:
            return [JRPG.data.armors.get(id) for id in sorted(self._armors.keys())]
        else:
            return []

    def equip_items(self) -> List[Any]:
        return self.weapons() + self.armors()

    def all_items(self) -> List[Any]:
        return self.items() + self.equip_items()

    def item_container(self, item_class: Any) -> Optional[Dict[int, int]]: # TODO: 
        if item_class == "items":
            return self._items
        elif item_class == "weapons":
            return self._weapons
        elif item_class == "armors":
            return self._armors
        else:
            return None

    def setup_starting_members(self) -> None:
        if JRPG.data and JRPG.data.system:
            self._actors = JRPG.data.system.get_or('party_members', [1]) # type: ignore
    
    #--------------------------------------------------------------------------
    # * Get Party Name
    #    If there is only one, returns the actor's name.
    #    If there are more, returns "XX's Party".
    #--------------------------------------------------------------------------
    def name(self) -> str:
        battle_members = self.battle_members()
        if len(battle_members) == 0:
            return ""
        
        leader = self.leader()
        if leader:
            name = leader.name
        else:
            name = "Leader"
        
        if len(battle_members) == 1:
            return name
        else:
            return "%s's Party" % name # TODO: Vocab.PartyName 

    def setup_battle_test(self) -> None:
        self.setup_battle_test_members()
        self.setup_battle_test_items()

    def setup_battle_test_members(self) -> None:
        if JRPG.data and JRPG.data.system and JRPG.objects and JRPG.objects.actors:
            test_battlers = JRPG.data.system.get("test_battlers") or []
            for battler in test_battlers:
                actor = JRPG.objects.actors[battler.actor_id]
                if actor:
                    actor.change_level(battler.level, False)
                    actor.init_equips(battler.equips)
                    actor.recover_all()
                    self.add_actor(actor._actor_id)

    def setup_battle_test_items(self) -> None:
        if JRPG.data and JRPG.data.items:
            for name, item in JRPG.data.items.all().items():
                if item and not item.get('name'):
                    self.gain_item(item, self.max_item_number(item))

    def highest_level(self) -> Optional[int]:
        levels = [actor.level() for actor in self.members()]
        return max(levels) if levels else None

    def add_actor(self, actor_id: int) -> None:
        if self._actors is not None:
            if actor_id not in self._actors:
                self._actors.append(actor_id)
            
            if JRPG.objects:
                if JRPG.objects.player:
                    JRPG.objects.player.refresh()
                if JRPG.objects.map:
                    JRPG.objects.map.need_refresh = True

    def remove_actor(self, actor_id: int) -> None:
        if self._actors:
            if actor_id in self._actors:
                self._actors.remove(actor_id)
            
            if JRPG.objects:
                if JRPG.objects.player:
                    JRPG.objects.player.refresh()
                if JRPG.objects.map:
                    JRPG.objects.map.need_refresh = True

    def gain_gold(self, amount: int) -> None:
        self._gold = max(0, min(self._gold + amount, self.max_gold()))

    def lose_gold(self, amount: int) -> None:
        self.gain_gold(-amount)

    def max_gold(self) -> int:
        return 99999999

    def increase_steps(self) -> None:
        self._steps += 1

    def item_number(self, item: Any) -> int:
        container = self.item_container(item.__name__)
        return container.get(item.id, 0) if container else 0

    def max_item_number(self, item: Any) -> int:
        return 99

    def item_max(self, item: Any) -> bool:
        return self.item_number(item) >= self.max_item_number(item)
    
    #--------------------------------------------------------------------------
    # * Determine Item Possession Status
    #     include_equip : Include equipped items
    #--------------------------------------------------------------------------
    def has_item(self, item: Any, include_equip: bool = False) -> bool:
        if self.item_number(item) > 0:
            return True
        return self.members_equip_include(item) if include_equip else False

    def members_equip_include(self, item: Any) -> bool:
        return any(item in actor.equips() for actor in self.members())
    
    #--------------------------------------------------------------------------
    # * Increase/Decrease Items
    #     include_equip : Include equipped items
    #--------------------------------------------------------------------------
    def gain_item(self, item: Any, amount: int, include_equip: bool = False) -> None:
        container = self.item_container(item.__name__)
        if container is None:
            return
        last_number = self.item_number(item)
        new_number = last_number + amount
        container[item.id] = max(0, min(new_number, self.max_item_number(item)))
        if container[item.id] == 0:
            container.pop(item.id, None)
        if include_equip and new_number < 0:
            self.discard_members_equip(item, -new_number)
        
        if JRPG.objects and JRPG.objects.map:
            JRPG.objects.map.need_refresh = True

        

    def discard_members_equip(self, item: Any, amount: int) -> None:
        n = amount
        for actor in self.members():
            while n > 0 and item in actor.equips():
                actor.discard_equip(item)
                n -= 1
    
    #--------------------------------------------------------------------------
    # * Lose Items
    #     include_equip : Include equipped items
    #--------------------------------------------------------------------------
    def lose_item(self, item: Any, amount: int, include_equip: bool = False) -> None:
        self.gain_item(item, -amount, include_equip)
    
    #--------------------------------------------------------------------------
    # * Consume Items
    #    If the specified object is a consumable item, the number in investory
    #    will be reduced by 1.
    #--------------------------------------------------------------------------
    def consume_item(self, item: Any) -> None:
        if item.__name__ == "items" and item.consumable:
            self.lose_item(item, 1)

    def usable(self, item: Any) -> bool:
        return any(actor.usable(item) for actor in self.members())

    def inputable(self) -> bool:
        return any(actor.inputable() for actor in self.members())

    def all_dead(self) -> bool:
        return super().all_dead() and ((JRPG.objects and JRPG.objects.party is not None and JRPG.objects.party.in_battle) or len(self.members()) > 0)

    def on_player_walk(self) -> None:
        for actor in self.members():
            actor.on_player_walk()

    def menu_actor(self) -> Any:
        actor = JRPG.objects and JRPG.objects.actors and JRPG.objects.actors[self._menu_actor_id]
        return actor or (self.members()[0] if self.members() else None)

    def set_menu_actor(self, actor: Any) -> None:
        self._menu_actor_id = actor.id

    def menu_actor_next(self) -> None:
        members = self.members()
        if not members:
            return
        current_actor = self.menu_actor()
        index = members.index(current_actor) if current_actor in members else -1
        index = (index + 1) % len(members)
        self.set_menu_actor(members[index])

    def menu_actor_prev(self) -> None:
        members = self.members()
        if not members:
            return
        current_actor = self.menu_actor()
        index = members.index(current_actor) if current_actor in members else 1
        index = (index + len(members) - 1) % len(members)
        self.set_menu_actor(members[index])

    def target_actor(self) -> Any:
        return JRPG.get_actor(self._target_actor_id) or (self.members()[0] if self.members() else None)

    def set_target_actor(self, actor: Any) -> None:
        self._target_actor_id = actor.id

    def swap_order(self, index1: int, index2: int) -> None:
        if self._actors:
            if 0 <= index1 < len(self._actors) and 0 <= index2 < len(self._actors):
                self._actors[index1], self._actors[index2] = self._actors[index2], self._actors[index1]
            if JRPG.objects and JRPG.objects.player:
                JRPG.objects.player.refresh()

    def characters_for_savefile(self) -> List[List[Any]]:
        return [[actor.character_name, actor.character_index] for actor in self.battle_members()]

    def party_ability(self, ability_id: int) -> bool:
        return any(actor.party_ability(ability_id) for actor in self.battle_members())

    def encounter_half(self) -> bool:
        return self.party_ability(self.ABILITY_ENCOUNTER_HALF)

    def encounter_none(self) -> bool:
        return self.party_ability(self.ABILITY_ENCOUNTER_NONE)

    def cancel_surprise(self) -> bool:
        return self.party_ability(self.ABILITY_CANCEL_SURPRISE)

    def raise_preemptive(self) -> bool:
        return self.party_ability(self.ABILITY_RAISE_PREEMPTIVE)

    def gold_double(self) -> bool:
        return self.party_ability(self.ABILITY_GOLD_DOUBLE)

    def drop_item_double(self) -> bool:
        return self.party_ability(self.ABILITY_DROP_ITEM_DOUBLE)

    def rate_preemptive(self, troop_agi: int) -> float:
        multiplier = 4 if self.raise_preemptive() else 1
        base_rate = 0.05 if self.agi() >= troop_agi else 0.03
        return base_rate * multiplier

    def rate_surprise(self, troop_agi: int) -> float:
        if self.cancel_surprise():
            return 0
        return 0.03 if self.agi() >= troop_agi else 0.05

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the party's state."""
        return {
            "actors": self._actors,
            # TODO: save inventory, gold, steps, etc.
        }

    def from_dict(self, data: Dict[str, Any]):
        """Loads the party's state from a dictionary."""
        self._actors = data.get("actors", [])