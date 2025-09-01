# scenes/geometry_dash_scene.py
# A Geometry Dash clone using the cpgame framework

from gint import *
try:
    from typing import Optional, Tuple, List, Dict, Any
except:                         # MicroPython or stripped env
    pass

# Engine imports
from cpgame.engine.scene import Scene
from cpgame.engine.geometry import Vec2, Rect
from cpgame.engine.animation import AnimationState

# --- Constants ---
# Player states
STATE_NORMAL, STATE_JUMPING, STATE_DEAD, STATE_WIN = 0, 1, 2, 3

# Block types
BLOCK_EMPTY, BLOCK_GROUND, BLOCK_PLATFORM, BLOCK_SPIKE, BLOCK_BOUNCE, BLOCK_WIN = 0, 1, 2, 3, 4, 5

# Physics
GRAVITY = 800.0
JUMP_FORCE = -350.0
PLAYER_SPEED = 200.0
GROUND_LEVEL = 160  # Fixed ground level
PLAYER_SIZE = 16
BLOCK_SIZE = 20

# Colors
COLOR_PLAYER = C_RGB(31, 15, 0)      # Orange
COLOR_GROUND = C_RGB(10, 10, 10)     # Dark gray
COLOR_PLATFORM = C_RGB(20, 20, 20)   # Gray
COLOR_SPIKE = C_RGB(31, 0, 0)        # Red
COLOR_BOUNCE = C_RGB(0, 31, 0)       # Green
COLOR_WIN = C_RGB(31, 31, 0)         # Yellow
COLOR_BG = C_RGB(5, 5, 15)           # Dark blue

class Player:
    def __init__(self):
        self.pos = Vec2(50, GROUND_LEVEL - PLAYER_SIZE)
        self.velocity = Vec2(0, 0)
        self.state = STATE_NORMAL
        self.on_ground = False
        self.jump_buffer = 0
        self.size = PLAYER_SIZE

    def update(self, dt: float):
        # Handle jump buffering
        if self.jump_buffer > 0:
            self.jump_buffer -= dt
        
        # Apply gravity
        if not self.on_ground:
            self.velocity.y += GRAVITY * dt
        
        # Update position
        self.pos.y += self.velocity.y * dt
        
        # Ground collision (basic)
        ground_y = GROUND_LEVEL - self.size
        if self.pos.y >= ground_y:
            self.pos.y = ground_y
            self.velocity.y = 0
            self.on_ground = True
        else:
            self.on_ground = False

    def jump(self):
        if self.on_ground or self.jump_buffer > 0:
            self.velocity.y = JUMP_FORCE
            self.on_ground = False
            self.jump_buffer = 0
            self.state = STATE_JUMPING

    def get_rect(self) -> Rect:
        return Rect(self.pos.x, self.pos.y, self.size, self.size)

class Block:
    def __init__(self, x: float, y: float, block_type: int, width: int = 1, height: int = 1):
        self.pos = Vec2(x, y)
        self.type = block_type
        self.width = width * BLOCK_SIZE
        self.height = height * BLOCK_SIZE
        
    def get_rect(self) -> Rect:
        return Rect(self.pos.x, self.pos.y, self.width, self.height)
    
    def get_color(self) -> int:
        if self.type == BLOCK_GROUND:
            return COLOR_GROUND
        elif self.type == BLOCK_PLATFORM:
            return COLOR_PLATFORM
        elif self.type == BLOCK_SPIKE:
            return COLOR_SPIKE
        elif self.type == BLOCK_BOUNCE:
            return COLOR_BOUNCE
        elif self.type == BLOCK_WIN:
            return COLOR_WIN
        return C_WHITE

class GeoDashScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.player = Player()
        self.blocks: List[Block] = []
        self.camera_x = 0.0
        self.game_time = 0.0
        self.level_complete = False
        self.death_timer = 0.0
        self.spawn_x = 0.0
        
    def create(self):
        """Initialize the game state"""
        print("GeometryDash: Creating...")
        
        # Reset player
        self.player = Player()
        self.camera_x = 0.0
        self.game_time = 0.0
        self.level_complete = False
        self.death_timer = 0.0
        self.spawn_x = 0.0
        
        # Create a simple level
        self.create_level()
    
    def create_level(self):
        """Generate the level geometry"""
        self.blocks = []
        
        # Create ground blocks
        for i in range(0, 100):  # Long ground
            x = i * BLOCK_SIZE
            y = GROUND_LEVEL
            self.blocks.append(Block(x, y, BLOCK_GROUND))
        
        # Add some platforms and obstacles
        level_data = [
            # (x_grid, y_grid, type, width, height)
            (8, 3, BLOCK_PLATFORM, 2, 1),   # Platform
            (12, 4, BLOCK_SPIKE, 1, 1),     # Spike
            (14, 3, BLOCK_PLATFORM, 3, 1),  # Platform
            (18, 1, BLOCK_SPIKE, 1, 1),     # Spike
            (20, 2, BLOCK_PLATFORM, 2, 1),  # High platform
            (24, 4, BLOCK_SPIKE, 1, 1),     # Spike
            (26, 3, BLOCK_BOUNCE, 1, 1),    # Bounce pad
            (30, 4, BLOCK_PLATFORM, 4, 1),  # Long platform
            (36, 3, BLOCK_SPIKE, 1, 1),     # Spike
            (38, 2, BLOCK_PLATFORM, 2, 2),  # Tall platform
            (42, 4, BLOCK_SPIKE, 1, 1),     # Spike
            (45, 3, BLOCK_BOUNCE, 1, 1),    # Bounce pad
            (50, 1, BLOCK_PLATFORM, 3, 1),  # High platform
            (55, 3, BLOCK_SPIKE, 1, 1),     # Spike
            (60, 3, BLOCK_WIN, 2, 3),       # Win block (tall)
        ]
        
        for x_grid, y_grid, block_type, width, height in level_data:
            x = x_grid * BLOCK_SIZE
            y = GROUND_LEVEL - (y_grid * BLOCK_SIZE)
            self.blocks.append(Block(x, y, block_type, width, height))
    
    def update(self, dt: float) -> Optional[str]:
        """Update game logic"""
        
        # Handle input
        if self.input.exit:
            return "EXIT_GAME"
        
        # Handle death state
        if self.player.state == STATE_DEAD:
            self.death_timer += dt
            if self.death_timer > 1.5:  # Respawn after 1.5 seconds
                self.respawn_player()
            return None
        
        # Handle win state
        if self.player.state == STATE_WIN:
            if self.input.shift or self.input.up:
                # Restart level
                self.create()
            return None
        
        # Jump input
        if self.input.shift or self.input.up:
            if self.player.jump_buffer <= 0:  # Prevent multiple jumps from one press
                self.player.jump()
                self.player.jump_buffer = 0.2  # Prevent immediate re-jump
        
        # Update game time
        self.game_time += dt
        
        # Auto-move player forward
        self.player.pos.x += PLAYER_SPEED * dt
        
        # Update player physics
        self.player.update(dt)
        
        # Update camera to follow player
        self.camera_x = self.player.pos.x - 100  # Keep player 100px from left edge
        
        # Check collisions
        self.check_collisions()
        
        # Reset jump state if on ground
        if self.player.on_ground and self.player.state == STATE_JUMPING:
            self.player.state = STATE_NORMAL
        
        return None
    
    def check_collisions(self):
        """Check player collision with blocks"""
        player_rect = self.player.get_rect()
        
        for block in self.blocks:
            if not player_rect.intersects(block.get_rect()):
                continue
                
            if block.type == BLOCK_SPIKE:
                # Death
                self.player.state = STATE_DEAD
                self.death_timer = 0.0
                return
                
            elif block.type == BLOCK_WIN:
                # Victory
                self.player.state = STATE_WIN
                self.level_complete = True
                return
                
            elif block.type == BLOCK_BOUNCE:
                # Bounce pad - super jump
                if self.player.velocity.y >= 0:  # Only if falling/on ground
                    self.player.velocity.y = JUMP_FORCE * 1.5
                    self.player.on_ground = False
                    
            elif block.type in (BLOCK_GROUND, BLOCK_PLATFORM):
                # Platform collision - simple top collision
                if self.player.velocity.y > 0 and player_rect.bottom > block.get_rect().top:
                    # Landing on top of platform
                    if player_rect.bottom - block.get_rect().top < 10:  # Close to top
                        self.player.pos.y = block.get_rect().top - self.player.size
                        self.player.velocity.y = 0
                        self.player.on_ground = True
    
    def respawn_player(self):
        """Respawn the player at the last safe position"""
        self.player = Player()
        self.player.pos.x = max(50, self.spawn_x)  # Don't go backwards
        self.player.state = STATE_NORMAL
        self.death_timer = 0.0
    
    def draw(self, frame_time_ms: int):
        """Render the game"""
        
        # Clear background
        dclear(COLOR_BG)
        
        # Draw blocks
        for block in self.blocks:
            block_rect = block.get_rect()
            # Only draw blocks that are on screen
            screen_x = block_rect.x - self.camera_x
            if screen_x > -BLOCK_SIZE and screen_x < DWIDTH + BLOCK_SIZE:
                drect(
                    int(screen_x), 
                    int(block_rect.y), 
                    int(screen_x + block_rect.w - 1), 
                    int(block_rect.y + block_rect.h - 1), 
                    block.get_color()
                )
        
        # Draw player
        if self.player.state != STATE_DEAD:
            player_rect = self.player.get_rect()
            screen_x = player_rect.x - self.camera_x
            
            # Player color changes based on state
            player_color = COLOR_PLAYER
            if self.player.state == STATE_JUMPING:
                player_color = C_RGB(31, 31, 15)  # Lighter when jumping
            elif self.player.state == STATE_WIN:
                player_color = C_RGB(15, 31, 15)  # Green when winning
            
            # Draw player as a square that rotates based on position
            rotation_angle = int(self.player.pos.x / 5) % 4  # Simple rotation effect
            if rotation_angle == 0:
                drect(int(screen_x), int(player_rect.y), 
                     int(screen_x + player_rect.w - 1), int(player_rect.y + player_rect.h - 1), 
                     player_color)
            else:
                # Draw a rotated-looking square (just a diamond shape)
                center_x = int(screen_x + player_rect.w // 2)
                center_y = int(player_rect.y + player_rect.h // 2)
                size = player_rect.w // 2
                # Draw diamond
                for i in range(-size, size + 1):
                    for j in range(-size + abs(i), size - abs(i) + 1):
                        dpixel(center_x + i, center_y + j, player_color)
        
        # Draw UI
        self.draw_ui(frame_time_ms)
    
    def draw_ui(self, frame_time_ms: int):
        """Draw the user interface"""
        # Draw ground level line for reference
        ground_screen_y = GROUND_LEVEL
        dline(0, ground_screen_y, DWIDTH - 1, ground_screen_y, C_RGB(15, 15, 15))
        
        # Draw game info
        if self.player.state == STATE_DEAD:
            dtext_opt(DWIDTH // 2 - 40, DHEIGHT // 2, C_WHITE, C_NONE, 
                     DTEXT_CENTER, DTEXT_MIDDLE, "YOU DIED!", -1)
            dtext_opt(DWIDTH // 2 - 50, DHEIGHT // 2 + 15, C_WHITE, C_NONE, 
                     DTEXT_CENTER, DTEXT_MIDDLE, "Respawning...", -1)
        elif self.player.state == STATE_WIN:
            dtext_opt(DWIDTH // 2 - 40, DHEIGHT // 2, C_RGB(31, 31, 0), C_NONE, 
                     DTEXT_CENTER, DTEXT_MIDDLE, "LEVEL COMPLETE!", -1)
            dtext_opt(DWIDTH // 2 - 60, DHEIGHT // 2 + 15, C_WHITE, C_NONE, 
                     DTEXT_CENTER, DTEXT_MIDDLE, "Press SHIFT to restart", -1)
        
        # Draw progress bar at top
        progress = min(self.player.pos.x / (60 * BLOCK_SIZE), 1.0)  # Level is ~60 blocks long
        progress_width = int(DWIDTH * progress)
        drect(0, 0, progress_width, 3, C_RGB(0, 31, 0))
        drect(progress_width, 0, DWIDTH - 1, 3, C_RGB(10, 10, 10))
        
        # Draw instructions
        dtext_opt(5, 5, C_WHITE, C_NONE, DTEXT_LEFT, DTEXT_TOP, 
                 "SHIFT/UP: Jump", -1)
        dtext_opt(5, 20, C_WHITE, C_NONE, DTEXT_LEFT, DTEXT_TOP, 
                 f"Time: {self.game_time:.1f}s", -1)
        
        # Draw legend
        legend_y = DHEIGHT - 60
        dtext_opt(5, legend_y, C_WHITE, C_NONE, DTEXT_LEFT, DTEXT_TOP, "Legend:", -1)
        
        # Color squares with labels
        legend_items = [
            (COLOR_GROUND, "Ground"),
            (COLOR_PLATFORM, "Platform"),
            (COLOR_SPIKE, "Spike"),
            (COLOR_BOUNCE, "Bounce"),
            (COLOR_WIN, "Win")
        ]
        
        for i, (color, label) in enumerate(legend_items):
            y = legend_y + 12 + i * 8
            drect(5, y, 10, y + 5, color)
            dtext_opt(15, y, C_WHITE, C_NONE, DTEXT_LEFT, DTEXT_TOP, label, -1)
        
        # Debug info (if needed)
        # dtext_opt(DWIDTH - 100, 5, C_WHITE, C_NONE, DTEXT_LEFT, DTEXT_TOP, 
        #          f"FT: {frame_time_ms}ms", -1)
        # dtext_opt(DWIDTH - 100, 20, C_WHITE, C_NONE, DTEXT_LEFT, DTEXT_TOP, 
        #          f"Pos: {int(self.player.pos.x)},{int(self.player.pos.y)}", -1)