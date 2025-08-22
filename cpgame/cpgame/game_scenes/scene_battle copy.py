# cpgame/game_scenes/scene_battle.py
from gint import *
import random
from cpgame.game_objects.actor import GameBattler
from cpgame.game_scenes._scenes_base import SceneBase
from cpgame.systems.jrpg import JRPG
from cpgame.engine.logger import log

# --- Layout Constants ---
ENEMY_AREA_H = DHEIGHT // 2
PLAYER_AREA_Y = ENEMY_AREA_H
ACTION_BOX_W, ACTION_BOX_H = 150, 150
C_YELLOW = 0b00000_111111_11111

class SceneBattle(SceneBase):
    """A lightweight, turn-based battle scene with action minigames."""
    
    def __init__(self, game, enemy_id):
        super().__init__(game)
        self._enemy_id = enemy_id
        
        # --- State Machine ---
        # States: START, PLAYER_TURN, PLAYER_ACTION, ENEMY_TURN, MINIGAME, WIN, LOSE
        self._state = "START"
        self._command_index = 0
        
        # --- Battle Objects ---
        self.player = JRPG.objects.party.leader() if JRPG.objects else None
        self.enemy = None # Will be an instance of Game_Battler
        
        # --- Minigame State ---
        self._minigame_active = False
        self._player_box_x = 0
        self._projectiles = []
        self._minigame_timer = 0  # Timer to end minigame
        self._minigame_duration = 6* 1000  # 6 seconds in milliseconds
        
        # --- Difficulty Settings ---
        self._difficulty = {
            'projectile_count': {'min': 2, 'max': 6},
            'projectile_speed': {'min': 2, 'max': 8},
            'projectile_size': {'min': 3, 'max': 8},
            'spawn_frequency': {'min': 200, 'max': 800}  # milliseconds
        }
        self._last_spawn_time = 0

    def create(self):
        log("SceneBattle: Created for enemy ID", self._enemy_id)
        if JRPG.data:
            with JRPG.data.enemies.load(self._enemy_id) as enemy_data:
                if enemy_data:
                    # We can use Game_Battler directly for a simple enemy
                    self.enemy = GameBattler()
                    self.enemy._data = enemy_data # Attach data
                    self.enemy.name = enemy_data.name
                    self.enemy.hp = enemy_data.params[0]
                    # self.enemy.mhp = enemy_data.params[0]  # Set max HP
                    # self.enemy.atk = enemy_data.params[2] if len(enemy_data.params) > 2 else 10  # Fixed attack stat
                    # self.enemy.defe = enemy_data.params[3] if len(enemy_data.params) > 3 else 5  # Defense stat

        if not self.enemy:
            log("ERROR: Could not load enemy data. Aborting battle.")
            if JRPG.game:
                    self.draw_loading_screen()
                    from cpgame.game_scenes.scene_map import SceneMap
                    JRPG.game.change_scene(SceneMap)
            return
            
        self._state = "PLAYER_TURN"

    def update(self, dt):
        self.input.update()
        
        if self._state == "PLAYER_TURN":
            self.update_player_command_selection()
        elif self._state == "MINIGAME":
            self.update_minigame(dt)
        elif self._state == "ENEMY_TURN":
            self.execute_enemy_turn()
        elif self._state == "WIN":
            self.handle_victory()
        elif self._state == "LOSE":
            self.handle_defeat()

    def draw(self, frame_time_ms):
        dclear(C_BLACK)
        self.draw_enemy_area()
        self.draw_player_area()

        if self._state == "MINIGAME":
            self.draw_minigame()
        elif self._state == "WIN":
            self.draw_victory_message()
        elif self._state == "LOSE":
            self.draw_defeat_message()

    # --- State Updates ---

    def update_player_command_selection(self):
        if self.input.up: self._command_index = max(0, self._command_index - 1)
        if self.input.down: self._command_index = min(2, self._command_index + 1)
        
        if self.input.interact:
            if self._command_index == 0: # Attack
                self.player_attack()
            elif self._command_index == 1: # Guard
                # For now, guard just skips turn
                self._state = "ENEMY_TURN"
            elif self._command_index == 2: # Flee
                if JRPG.game:
                    self.draw_loading_screen()
                    from cpgame.game_scenes.scene_map import SceneMap
                    JRPG.game.change_scene(SceneMap)

    def update_minigame(self, dt):
        self._minigame_timer += int(dt* 1000)
        
        # Move player box
        if self.input.dx != 0:
            self._player_box_x += self.input.dx * 5
            self._player_box_x = max(self._player_box_x, (DWIDTH - ACTION_BOX_W) // 2)
            self._player_box_x = min(self._player_box_x, (DWIDTH + ACTION_BOX_W) // 2 - 20)

        # Update projectiles
        hit = False
        for p in self._projectiles:
            p['y'] += 5 # Move down
            if p['y'] > PLAYER_AREA_Y + ACTION_BOX_H: 
                p['y'] = PLAYER_AREA_Y - random.randint(0, 100) # Reset to top
            
            # Collision check
            if (p['y'] > PLAYER_AREA_Y + ACTION_BOX_H - 20 and
                p['y'] < PLAYER_AREA_Y + ACTION_BOX_H and
                self._player_box_x < p['x'] + 5 and  # Improved collision detection
                self._player_box_x + 20 > p['x']):
                hit = True
                break
        
        # Handle hit or minigame timeout
        if hit and self.player and self.enemy:
            damage = max(1, self.enemy.atk - (self.player.defe if hasattr(self.player, 'defe') else 0))
            self.player.hp -= damage
            log("Player hit! Took", damage, "damage. HP:", self.player.hp)
            self.end_minigame()
        elif self._minigame_timer >= self._minigame_duration:
            log("Player successfully dodged enemy attack!")
            self.end_minigame()

    def end_minigame(self):
        """Helper method to clean up and end the minigame"""
        self._minigame_active = False
        self._minigame_timer = 0
        if self.player and self.player.hp <= 0:
            self._state = "LOSE"
        else:
            self._state = "PLAYER_TURN"

    # --- Logic ---

    def player_attack(self):
        if self.player and self.enemy:
            damage = max(1, self.player.atk - (self.enemy.defe if hasattr(self.enemy, 'defe') else 0))
            self.enemy.hp -= damage
            log("Player attacks for", damage, "damage! Enemy HP:", self.enemy.hp)
            
            if self.enemy.hp <= 0:
                self._state = "WIN"
            else:
                self._state = "ENEMY_TURN"

    def execute_enemy_turn(self):
        log("Enemy's turn.")
        # Start the minigame
        self._minigame_active = True
        self._minigame_timer = 0
        self._player_box_x = DWIDTH // 2 - 10
        self._projectiles = []
        
        # Create projectiles with better spacing
        for i in range(3):  # Reduced number for better gameplay
            self._projectiles.append({
                'x': random.randint((DWIDTH - ACTION_BOX_W) // 2 + 10, 
                                  (DWIDTH + ACTION_BOX_W) // 2 - 15),
                'y': PLAYER_AREA_Y - random.randint(20, 80)
            })
        
        self._state = "MINIGAME"  # Fixed state name

    def handle_victory(self):
        """Handle victory state - wait for input then return to previous scene"""
        if self.input.interact:
            log("Battle won! Returning to previous scene.")
            from cpgame.game_scenes.scene_map import SceneMap
            # Here you might want to give rewards, experience, etc.
            if JRPG.game:
                    self.draw_loading_screen()
                    from cpgame.game_scenes.scene_map import SceneMap
                    JRPG.game.change_scene(SceneMap)

    def handle_defeat(self):
        """Handle defeat state - wait for input then return to previous scene"""
        if self.input.interact:
            log("Battle lost! Returning to previous scene.")
            # Here you might want to handle game over logic
            from cpgame.game_scenes.scene_map import SceneMap
            if JRPG.game:
                    self.draw_loading_screen()
                    from cpgame.game_scenes.scene_map import SceneMap
                    JRPG.game.change_scene(SceneMap)

    # --- Drawing ---

    def draw_enemy_area(self):
        drect(0, 0, DWIDTH-1, ENEMY_AREA_H-1, C_RGB(10,10,15))
        if self.enemy:
            dtext_opt(DWIDTH//2, 50, C_WHITE, C_NONE, DTEXT_CENTER, DTEXT_TOP, self.enemy.name, -1)
            hp_text = "HP: {} / {}".format(self.enemy.hp, self.enemy.mhp)
            dtext_opt(DWIDTH//2, 80, C_WHITE, C_NONE, DTEXT_CENTER, DTEXT_TOP, hp_text, -1)
    
    def draw_player_area(self):
        if self._state == "PLAYER_TURN":
            commands = ["Attack", "Guard", "Flee"]
            for i, cmd in enumerate(commands):
                color = C_YELLOW if i == self._command_index else C_WHITE
                dtext(20, PLAYER_AREA_Y + 20 + i * 30, color, cmd)
        
        # Always show player HP
        if self.player:
            player_hp_text = "Player HP: {}".format(self.player.hp)
            dtext(20, PLAYER_AREA_Y + 120, C_WHITE, player_hp_text)

    def draw_minigame(self):
        # Draw instructions
        dtext_opt(DWIDTH//2, PLAYER_AREA_Y - 20, C_WHITE, C_NONE, DTEXT_CENTER, DTEXT_TOP, "Dodge the projectiles!", -1)
        
        # Draw the action box
        box_x = (DWIDTH - ACTION_BOX_W) // 2
        drect_border(box_x, PLAYER_AREA_Y, box_x + ACTION_BOX_W, PLAYER_AREA_Y + ACTION_BOX_H, C_NONE, 1, C_WHITE)

        # Draw player
        drect(self._player_box_x, PLAYER_AREA_Y + ACTION_BOX_H - 20, self._player_box_x + 20, PLAYER_AREA_Y + ACTION_BOX_H, C_BLUE)

        # Draw projectiles
        for p in self._projectiles:
            drect(p['x'], p['y'], p['x'] + 5, p['y'] + 10, C_RED)
        
        # Draw timer
        time_left = max(0, self._minigame_duration - self._minigame_timer) / 1000.0
        timer_text = "Time: {:.1f}s".format(time_left)
        dtext(DWIDTH - 100, PLAYER_AREA_Y + 10, C_WHITE, timer_text)

    def draw_victory_message(self):
        dtext_opt(DWIDTH//2, DHEIGHT//2, C_WHITE, C_NONE, DTEXT_CENTER, DTEXT_MIDDLE, "VICTORY!", -1)
        dtext_opt(DWIDTH//2, DHEIGHT//2 + 30, C_WHITE, C_NONE, DTEXT_CENTER, DTEXT_MIDDLE, "Press [Action] to continue", -1)

    def draw_defeat_message(self):
        dtext_opt(DWIDTH//2, DHEIGHT//2, C_RED, C_NONE, DTEXT_CENTER, DTEXT_MIDDLE, "DEFEAT!", -1)
        dtext_opt(DWIDTH//2, DHEIGHT//2 + 30, C_WHITE, C_NONE, DTEXT_CENTER, DTEXT_MIDDLE, "Press [Action] to continue", -1)