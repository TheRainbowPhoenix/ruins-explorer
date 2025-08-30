# cpgame/game_scenes/scene_battle.py
from gint import *
import random
from cpgame.game_objects.actor import GameBattler
from cpgame.game_scenes._scenes_base import SceneBase
from cpgame.systems.jrpg import JRPG, BATTLE_RESULT_WIN, BATTLE_RESULT_ESCAPE, BATTLE_RESULT_LOSE
from cpgame.engine.logger import log
from cpgame.modules.pakloader import PakProxy

# --- Layout Constants ---
ENEMY_AREA_H = DHEIGHT // 2
PLAYER_AREA_Y = ENEMY_AREA_H
ACTION_BOX_W, ACTION_BOX_H = 150, 150
C_YELLOW = 0b00000_111111_11111

class SceneBattle(SceneBase):
    """A lightweight, turn-based battle scene with action minigames."""
    
    def __init__(self, game, **kwargs):
        super().__init__(game)
        self._enemy_id = kwargs.get('enemy_id')
        self._can_escape = kwargs.get('can_escape', True)
        self._battle_end_callback = kwargs.get('battle_end_callback')
        self._result_variable_id = kwargs.get('result_var_id')
        
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
        self._player_box_y = 0  # For jumping/falling
        self._projectiles = []
        self._minigame_timer = 0  # Timer to end minigame
        self._minigame_duration = 3000  # 3 seconds in milliseconds
        
        # --- Player Movement State ---
        self._player_velocity_y = 0
        self._player_grounded = True
        self._player_invulnerable = False  # During down slash
        self._gravity = 0.5
        self._jump_strength = -11
        self._ground_level = ACTION_BOX_H - 20
        
        # --- Graze System ---
        self._graze_particles = []  # Visual feedback for grazing
        self._graze_text_timer = 0
        self._last_graze_time = 0
        
        # --- Difficulty Settings ---
        self._difficulty = {
            'projectile_count': {'min': 2, 'max': 6},
            'projectile_speed': {'min': 2, 'max': 8},
            'projectile_size': {'min': 3, 'max': 8},
            'spawn_frequency': {'min': 200, 'max': 800}  # milliseconds
        }
        self._last_spawn_time = 0
        self._background_drawn = False

    def create(self):
        log("SceneBattle: Created for enemy ID", self._enemy_id)
        if JRPG.data:
            with JRPG.data.enemies.load(self._enemy_id) as enemy_data:
                if enemy_data:
                    # We can use Game_Battler directly for a simple enemy
                    self.enemy = GameBattler()
                    self.enemy._data = enemy_data # Attach data
                    self.enemy.name = enemy_data.name
                    self.enemy._param_plus = enemy_data.params
                    self.enemy.battler_name = enemy_data.battler_name
                    # MHP, MMP, ATK, DEF, etc.

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
        self._background_drawn = False

    def update(self, dt):
        # self.input.update()
        
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

        if not self._background_drawn:
            self.draw_static_background()
            self._background_drawn = True
        
        self.draw_dynamic_elements()

    def draw_static_background(self):
        """
        Draws all elements that do not change during the battle.
        This is called ONLY ONCE to avoid slow operations.
        """
        log("Performing one-time static draw for battle scene.")
        
        dclear(C_BLACK)
        
        drect(0, 0, DWIDTH-1, ENEMY_AREA_H-1, C_RGB(10,10,15))
        
        if self.enemy and self.enemy.battler_name:
            size = 160 if self.enemy.battler_name == 'vorpal' else 64
            draw_x = (DWIDTH - size) // 2
            draw_y = 70
            clip_x_end = draw_x + size
            
            pak_proxy = PakProxy()
            pak_proxy.draw_from(draw_x, draw_y, 'enemies.pak', self.enemy.battler_name, clip_x_end)

    def draw_dynamic_elements(self):
        """
        Draws all elements that change frame-to-frame (text, cursors, minigame objects).
        """
        if self.enemy:
            # Clear ONLY the area where text will be drawn to avoid erasing the sprite
            drect(0, 10, DWIDTH - 1, 50, C_RGB(10,10,15)) # Top bar for text
            dtext_opt(DWIDTH//2, 10, C_WHITE, C_NONE, DTEXT_CENTER, DTEXT_TOP, self.enemy.name, -1)
            hp_text = "HP: {} / {}".format(self.enemy.hp, self.enemy.mhp)
            dtext_opt(DWIDTH//2, 30, C_WHITE, C_NONE, DTEXT_CENTER, DTEXT_TOP, hp_text, -1)
        
        # --- Player Area ---
        # Clear the entire bottom half for the player UI and minigame
        drect(0, PLAYER_AREA_Y, DWIDTH - 1, DHEIGHT - 1, C_BLACK)
        self.draw_player_area()

        # --- Conditional UI Elements ---
        if self._state == "MINIGAME":
            self.draw_minigame()
        elif self._state == "WIN":
            self.draw_victory_message()
        elif self._state == "LOSE":
            self.draw_defeat_message()
        
    # --- State Updates ---

    def _end_battle(self, result: int):
        """Common cleanup logic for ending the battle."""
        log("Battle ended with result:", result)
        if self._battle_end_callback:
            self._battle_end_callback(result)
        
        if self._result_variable_id is not None and JRPG.objects:
            JRPG.objects.variables[self._result_variable_id] = result
    
        # Return to the previous scene (the map)
        # self.game.return_scene()
        if JRPG.game:
            self.draw_loading_screen()
            from cpgame.game_scenes.scene_map import SceneMap
            JRPG.game.change_scene(SceneMap)

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
                self._end_battle(BATTLE_RESULT_ESCAPE)

    def update_minigame(self, dt):
        self._minigame_timer += int(dt * 1000)
        
        # Update graze text timer
        if self._graze_text_timer > 0:
            self._graze_text_timer -= dt
        
        # Handle player input
        box_x = (DWIDTH - ACTION_BOX_W) // 2
        
        # Horizontal movement
        if self.input.dx != 0:
            box_x = (DWIDTH - ACTION_BOX_W) // 2
            self._player_box_x += self.input.dx * 4  # Slightly slower for precision
            self._player_box_x = max(box_x, min(self._player_box_x, box_x + ACTION_BOX_W - 20))
        
        # Vertical movement - Jump and Down Slash
        if self.input.up and self._player_grounded:
            self._player_velocity_y = self._jump_strength
            self._player_grounded = False
            log("Player jumps!")
        elif self.input.down and not self._player_grounded:
            # Down slash - makes player invulnerable while falling
            self._player_velocity_y = 6  # Fast downward movement
            self._player_invulnerable = True
            log("Player performs down slash!")
        
        # Apply gravity and update vertical position
        if not self._player_grounded:
            self._player_velocity_y += self._gravity
            self._player_box_y += self._player_velocity_y
            
            # Check if landed
            if self._player_box_y >= self._ground_level:
                self._player_box_y = self._ground_level
                self._player_velocity_y = 0
                self._player_grounded = True
                self._player_invulnerable = False  # End invulnerability when landing
        
        # Spawn new projectiles
        if self._minigame_timer - self._last_spawn_time > random.randint(
            self._difficulty['spawn_frequency']['min'], 
            self._difficulty['spawn_frequency']['max']):
            self.spawn_projectile()
            self._last_spawn_time = self._minigame_timer

        # Update existing projectiles and check for grazing/collision
        hit = False
        projectiles_to_remove = []
        
        for i, p in enumerate(self._projectiles):
            # Move projectile down
            p['y'] += p['speed']
            
            # Remove if it goes past the action box
            if p['y'] > PLAYER_AREA_Y + ACTION_BOX_H:
                projectiles_to_remove.append(i)
                continue
            
            # Get player's current size based on jump height
            player_w, player_h = self.get_player_current_size()
            player_left = self._player_box_x
            player_right = self._player_box_x + player_w
            player_top = PLAYER_AREA_Y + self._player_box_y
            player_bottom = PLAYER_AREA_Y + self._player_box_y + player_h
            
            # Get projectile hitbox
            proj_left = p['x']
            proj_right = p['x'] + p['size']
            proj_top = p['y']
            proj_bottom = p['y'] + p['size']
            
            # Check for collision (only if not invulnerable)
            if (not self._player_invulnerable and
                player_left < proj_right and player_right > proj_left and
                player_top < proj_bottom and player_bottom > proj_top):
                hit = True
                break
            
            # Check for graze (very close but not touching) - only if no collision
            if not hit and not self._player_invulnerable:
                graze_distance = 8  # Glaze: Less than 8 pixels
                
                # Calculate distances between edges
                horizontal_gap = 0
                vertical_gap = 0
                
                if player_right <= proj_left:  # Player to the left
                    horizontal_gap = proj_left - player_right
                elif proj_right <= player_left:  # Player to the right
                    horizontal_gap = player_left - proj_right
                
                if player_bottom <= proj_top:  # Player above
                    vertical_gap = proj_top - player_bottom
                elif proj_bottom <= player_top:  # Player below
                    vertical_gap = player_top - proj_bottom
                
                # Graze if either gap is very small (but not overlapping)
                is_grazing = ((horizontal_gap > 0 and horizontal_gap <= graze_distance and 
                              player_top < proj_bottom and player_bottom > proj_top) or
                             (vertical_gap > 0 and vertical_gap <= graze_distance and 
                              player_left < proj_right and player_right > proj_left))
                
                if is_grazing and self._minigame_timer - self._last_graze_time > 100:
                    self.handle_graze(p)
                    self._last_graze_time = self._minigame_timer
        
        # Remove projectiles that went off screen
        for i in reversed(projectiles_to_remove):
            self._projectiles.pop(i)
        
        # Update graze particles
        particles_to_remove = []
        for i, particle in enumerate(self._graze_particles):
            particle['life'] -= int(dt * 1000)
            particle['x'] += particle['vel_x']  # Move with velocity
            particle['y'] += particle['vel_y']  # Float upward
            
            if particle['life'] <= 0:
                particles_to_remove.append(i)
        
        for i in reversed(particles_to_remove):
            self._graze_particles.pop(i)
        
        # Handle hit or minigame timeout
        if hit and self.player and self.enemy:
            damage = max(1, self.enemy.atk - (self.player.defe if hasattr(self.player, 'defe') else 0))
            self.player.hp -= damage
            log("Player hit! Took", damage, "damage. HP:", self.player.hp)
            self.end_minigame()
        elif self._minigame_timer >= self._minigame_duration:
            log("Player successfully survived the minigame!")
            self.end_minigame()
    
    def get_player_current_size(self) -> tuple[int, int]:
        """Calculates player hitbox size based on jump height. Smaller when higher."""
        base_size = 20
        min_jump_size = 5 # Size at the absolute peak of the jump (4x smaller area)

        if self._player_grounded:
            return base_size, base_size

        ground_y = self._ground_level # e.g., 130
        peak_y = 65.0 # Approximate peak height of a full jump

        # Calculate the total range of the jump.
        jump_height_range = ground_y - peak_y # e.g., 130 - 65 = 65
        if jump_height_range <= 0: return base_size, base_size # Avoid division by zero

        # Calculate the player's current progress within that range.
        #    This will be 0.0 at the peak and 1.0 on the ground.
        current_pos_in_range = self._player_box_y - peak_y
        progress = current_pos_in_range / jump_height_range
        
        # Clamp the progress between 0.0 and 1.0 to handle small hops or overshoots.
        progress = max(0.0, min(1.0, progress))

        # Interpolate the size based on the progress.
        #    size = min_size + progress * (max_size - min_size)
        size_range = base_size - min_jump_size
        current_size = int(min_jump_size + (progress * size_range))
        
        return current_size, current_size

    def handle_graze(self, projectile):
        """Handle grazing a projectile - heal player and show visual feedback"""
        if self.player:
            player_max_hp = getattr(self.player, 'mhp', 100)
            if self.player.hp < player_max_hp:
                # Dynamic healing based on current health percentage
                health_percentage = self.player.hp / player_max_hp
                
                if health_percentage <= 0.2:  # 20% or less HP
                    heal_amount = 4
                elif health_percentage <= 0.4:  # 40% or less HP
                    heal_amount = 3
                elif health_percentage <= 0.6:  # 60% or less HP
                    heal_amount = 2
                elif health_percentage <= 0.8:  # 80% or less HP
                    heal_amount = 2
                else:  # Above 80% HP
                    heal_amount = 1
                
                self.player.hp = min(player_max_hp, self.player.hp + heal_amount)
                log(f"Graze! Healed {heal_amount} HP (health was {health_percentage:.1%}). Current HP: {self.player.hp}")
                
                # Show "Graze" text
                self._graze_text_timer = 1000  # Show for 1 second
                
                # Add visual particle effect with lifetime counter
                self._graze_particles.append({
                    'x': projectile['x'] + projectile['size'] // 2,
                    'y': projectile['y'] + projectile['size'] // 2,
                    'life': 500,  # Will disappear after 10 updates
                    'vel_x': random.randint(-2, 2),  # Small random movement
                    'vel_y': random.randint(-3, -1)  # Float upward
                })

    

    def end_minigame(self):
        """Helper method to clean up and end the minigame"""
        self._minigame_active = False
        self._minigame_timer = 0
        if self.player and self.player.hp <= 0:
            self._state = "LOSE"
        else:
            self._state = "PLAYER_TURN"

    def spawn_projectile(self):
        """Spawn a new projectile with random properties based on difficulty"""
        box_x = (DWIDTH - ACTION_BOX_W) // 2
        
        # Random properties based on difficulty settings
        size = random.randint(
            self._difficulty['projectile_size']['min'],
            self._difficulty['projectile_size']['max']
        )
        speed = random.randint(
            self._difficulty['projectile_speed']['min'],
            self._difficulty['projectile_speed']['max']
        )
        
        # Spawn within the action box boundaries
        x = random.randint(box_x, box_x + ACTION_BOX_W - size)
        y = PLAYER_AREA_Y - random.randint(10, 50)  # Start just above the box
        
        self._projectiles.append({
            'x': x,
            'y': y,
            'size': size,
            'speed': speed
        })

    def calculate_difficulty(self):
        """Calculate minigame difficulty based on enemy minigame_difficulty and player health"""
        if not self.player or not self.enemy:
            return
            
        # Get enemy's minigame difficulty (1-5, where 0 = no minigame)
        base_difficulty = getattr(self.enemy._data, 'minigame_difficulty', 3) if hasattr(self.enemy, '_data') else 3
        
        # Skip minigame if difficulty is 0
        if base_difficulty == 0:
            log("Enemy has no minigame (difficulty 0)")
            return False  # Signal to skip minigame
        
        # Player health factor (lower HP = easier minigame for mercy)
        player_max_hp = getattr(self.player, 'mhp', self.player.hp)
        player_health_factor = self.player.hp / max(player_max_hp, 1)
        health_mercy = max(0.5, player_health_factor)  # At least 50% difficulty when low HP
        
        # Apply health mercy to base difficulty
        final_difficulty = base_difficulty * health_mercy
        
        log(f"Difficulty calculation: Base={base_difficulty}, Health factor={health_mercy:.2f}, Final={final_difficulty:.2f}")
        
        # Adjust settings based on final difficulty level
        if final_difficulty <= 1.5:  # Very Easy (1 * low health)
            self._difficulty['projectile_count'] = {'min': 1, 'max': 2}
            self._difficulty['projectile_speed'] = {'min': 1, 'max': 2}
            self._difficulty['projectile_size'] = {'min': 3, 'max': 4}
            self._difficulty['spawn_frequency'] = {'min': 800, 'max': 1200}
            self._minigame_duration = 8000  # 8 seconds (3x)
        elif final_difficulty <= 2.5:  # Easy (2 * health or 1 * full health)
            self._difficulty['projectile_count'] = {'min': 1, 'max': 3}
            self._difficulty['projectile_speed'] = {'min': 2, 'max': 3}
            self._difficulty['projectile_size'] = {'min': 4, 'max': 5}
            self._difficulty['spawn_frequency'] = {'min': 600, 'max': 900}
            self._minigame_duration = 9500  # 9.5 seconds (3x)
        elif final_difficulty <= 3.5:  # Normal (3 * health or 2 * full health)
            self._difficulty['projectile_count'] = {'min': 2, 'max': 4}
            self._difficulty['projectile_speed'] = {'min': 3, 'max': 4}
            self._difficulty['projectile_size'] = {'min': 4, 'max': 6}
            self._difficulty['spawn_frequency'] = {'min': 400, 'max': 700}
            self._minigame_duration = 12000  # 12 seconds (3x)
        elif final_difficulty <= 4.5:  # Hard (4 * health or 3 * full health)
            self._difficulty['projectile_count'] = {'min': 3, 'max': 5}
            self._difficulty['projectile_speed'] = {'min': 4, 'max': 6}
            self._difficulty['projectile_size'] = {'min': 5, 'max': 7}
            self._difficulty['spawn_frequency'] = {'min': 300, 'max': 500}
            self._minigame_duration = 20500  # 20.5 seconds (3x)
        else:  # Nightmare (5 * health or 4+ * full health)
            self._difficulty['projectile_count'] = {'min': 4, 'max': 9}
            self._difficulty['projectile_speed'] = {'min': 5, 'max': 9}
            self._difficulty['projectile_size'] = {'min': 6, 'max': 8}
            self._difficulty['spawn_frequency'] = {'min': 150, 'max': 500}
            self._minigame_duration = 24000  # 24 seconds (3x)
            
        return True  # Signal that minigame should proceed

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
        
        # Calculate difficulty and check if minigame should run
        should_run_minigame = self.calculate_difficulty()
        
        if not should_run_minigame:
            # Skip minigame, just do direct damage
            if self.player and self.enemy:
                damage = max(1, self.enemy.atk - (self.player.defe if hasattr(self.player, 'defe') else 0))
                self.player.hp -= damage
                log("Enemy attacks directly for", damage, "damage! Player HP:", self.player.hp)
                if self.player.hp <= 0:
                    self._state = "LOSE"
                else:
                    self._state = "PLAYER_TURN"
            return
        
        # Start the minigame
        self._minigame_active = True
        self._minigame_timer = 0
        self._last_spawn_time = 0
        self._last_graze_time = 0
        
        # Center player in the action box
        box_x = (DWIDTH - ACTION_BOX_W) // 2
        self._player_box_x = box_x + ACTION_BOX_W // 2 - 10
        self._player_box_y = self._ground_level
        self._player_velocity_y = 0
        self._player_grounded = True
        self._player_invulnerable = False
        self._graze_text_timer = 0
        self._graze_particles = []
        self._projectiles = []
        
        # Spawn initial projectiles based on difficulty
        initial_count = random.randint(
            self._difficulty['projectile_count']['min'],
            self._difficulty['projectile_count']['max']
        )
        
        for i in range(initial_count):
            self.spawn_projectile()
        
        self._state = "MINIGAME"  # Fixed state name

    def handle_victory(self):
        """Handle victory state - wait for input then return to previous scene"""
        if self.input.interact:
            log("Battle won! Returning to previous scene.")
            self._end_battle(BATTLE_RESULT_WIN)

    def handle_defeat(self):
        """Handle defeat state - wait for input then return to previous scene"""
        if self.input.interact:
            log("Battle lost! Returning to previous scene.")
            self._end_battle(BATTLE_RESULT_LOSE)

    # --- Drawing ---

    def draw_enemy_area(self):
        drect(0, 0, DWIDTH-1, ENEMY_AREA_H-1, C_RGB(10,10,15))
        if self.enemy:
            dtext_opt(DWIDTH//2, 20, C_WHITE, C_NONE, DTEXT_CENTER, DTEXT_TOP, self.enemy.name, -1)
            hp_text = "HP: {} / {}".format(self.enemy.hp, self.enemy.mhp)
            dtext_opt(DWIDTH//2, 40, C_WHITE, C_NONE, DTEXT_CENTER, DTEXT_TOP, hp_text, -1)

            # --- Cached Sprite Drawing ---
            # This block only runs ONCE per battle, or if a redraw is forced.
            if not self._background_drawn and self.enemy.battler_name:
                log("Drawing enemy sprite for the first time:", self.enemy.battler_name)
                
                # TODO: Placeholder sizes for assets
                size = 160 if self.enemy.battler_name == 'vorpal' else 64
                
                draw_x = (DWIDTH - size) // 2
                draw_y = 70 # Position it below the text
                clip_x_end = draw_x + size


                pak_proxy = PakProxy()
                
                # The last argument tells the proxy the max x-coordinate to draw to
                pak_proxy.draw_from(draw_x, draw_y, 'enemies.pak', self.enemy.battler_name, clip_x_end)
                
                del pak_proxy
                self._background_drawn = True
    
    def draw_player_area(self):
        if self._state == "PLAYER_TURN":
            commands = ["Attack", "Guard", "Flee"]
            for i, cmd in enumerate(commands):
                color = C_YELLOW if i == self._command_index else C_WHITE
                dtext(20, PLAYER_AREA_Y + 20 + i * 30, color, cmd)
        
        # Always show player HP
        if self.player:
            player_max_hp = getattr(self.player, 'mhp', self.player.hp)
            player_hp_text = "Player HP: {}/{}".format(self.player.hp, player_max_hp)
            dtext(5, DHEIGHT - 20, C_WHITE, player_hp_text)

    def draw_minigame(self):
        # Draw instructions
        drect(1,ENEMY_AREA_H - 25, DWIDTH-1, ENEMY_AREA_H - (25-12), C_RGB(10,10,15))
        dtext_opt(DWIDTH//2,ENEMY_AREA_H - 25, C_WHITE, C_NONE, DTEXT_CENTER, DTEXT_TOP, "Dodge!", -1)
        
        # Draw the action box
        box_x = (DWIDTH - ACTION_BOX_W) // 2
        drect_border(box_x, PLAYER_AREA_Y, box_x + ACTION_BOX_W, PLAYER_AREA_Y + ACTION_BOX_H, C_NONE, 1, C_WHITE)

        # Draw player
        player_w, player_h = self.get_player_current_size()
        player_draw_y = int(PLAYER_AREA_Y + self._player_box_y + (20 - player_h)) # Align to bottom
        if self._player_invulnerable:
            # Draw only border when invulnerable (down slash)
            drect_border(self._player_box_x, player_draw_y, self._player_box_x + player_w, player_draw_y + player_h, C_NONE, 1, C_BLUE)
        else:
            # Draw full player
            drect(self._player_box_x, player_draw_y, self._player_box_x + player_w, player_draw_y + player_h, C_BLUE)

        # Draw projectiles (only if they're within or near the action box)
        for p in self._projectiles:
            if p['y'] >= PLAYER_AREA_Y - 0 and p['y'] <= PLAYER_AREA_Y + ACTION_BOX_H + 10:
                drect(p['x'], p['y'], p['x'] + p['size'], p['y'] + p['size'], C_RED)
        
        # Draw graze particles
        for particle in self._graze_particles:
            # alpha = particle['life'] // 500.0  # Fade out
            # if alpha > 0:
            # Simple particle - could be enhanced with better graphics
            drect(particle['x'] - 2, particle['y'] - 2, particle['x'] + 2, particle['y'] + 2, C_YELLOW)
        
        # Draw "Graze" text if recently grazed
        if self._graze_text_timer > 0:
            dtext_opt(DWIDTH//2, PLAYER_AREA_Y + ACTION_BOX_H + 10, C_YELLOW, C_NONE, DTEXT_CENTER, DTEXT_TOP, "GRAZE!", -1)
        
        # Draw timer at bottom right
        time_left = max(0, self._minigame_duration - self._minigame_timer) / 1000.0
        timer_text = "Time: {:.1f}s".format(time_left)
        dtext_opt(DWIDTH - 5, DHEIGHT - 20, C_WHITE, C_NONE, DTEXT_RIGHT, DTEXT_TOP, timer_text, -1)
        
        # Draw difficulty indicator
        if self.player and self.enemy:
            base_difficulty = getattr(self.enemy._data, 'minigame_difficulty', 3) if hasattr(self.enemy, '_data') else 3
            player_max_hp = getattr(self.player, 'mhp', self.player.hp)
            player_health_factor = self.player.hp / max(player_max_hp, 1)
            final_difficulty = base_difficulty * max(0.5, player_health_factor)
            
            difficulty_names = ["", "Very Easy", "Easy", "Normal", "Hard", "Nightmare"]
            difficulty_name = difficulty_names[min(base_difficulty, 5)] if base_difficulty <= 5 else "Nightmare"
            
            if player_health_factor < 1.0:  # Show mercy if player is damaged
                difficulty_text = f"{difficulty_name} (Mercy: {player_health_factor:.1f}x)"
            else:
                difficulty_text = difficulty_name
            
            
            drect(1,PLAYER_AREA_Y - 12, DWIDTH-1, PLAYER_AREA_Y, C_RGB(10,10,15))
            dtext_opt(DWIDTH//2, PLAYER_AREA_Y - 12, C_YELLOW, C_NONE, DTEXT_CENTER, DTEXT_TOP, difficulty_text, -1)

    def draw_victory_message(self):
        dtext_opt(DWIDTH//2, DHEIGHT//2, C_WHITE, C_NONE, DTEXT_CENTER, DTEXT_MIDDLE, "VICTORY!", -1)
        dtext_opt(DWIDTH//2, DHEIGHT//2 + 30, C_WHITE, C_NONE, DTEXT_CENTER, DTEXT_MIDDLE, "Press [Action] to continue", -1)

    def draw_defeat_message(self):
        dtext_opt(DWIDTH//2, DHEIGHT//2, C_RED, C_NONE, DTEXT_CENTER, DTEXT_MIDDLE, "DEFEAT!", -1)
        dtext_opt(DWIDTH//2, DHEIGHT//2 + 30, C_WHITE, C_NONE, DTEXT_CENTER, DTEXT_MIDDLE, "Press [Action] to continue", -1)