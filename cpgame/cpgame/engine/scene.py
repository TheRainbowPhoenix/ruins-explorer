# engine/scene.py
# Defines the core Scene class and the SceneManager.

from cpgame.engine.systems import InputManager, Camera
from cpgame.engine.assets import AssetManager
try:
    from typing import Optional, List
    from cpgame.engine.game import Game
except:
    pass

class Scene:
    """
    The base class for all game states, inspired by Phaser.Scene.
    A Scene has a lifecycle: init -> create -> update/draw -> destroy.
    """
    def __init__(self, game: 'Game'):
        self.game = game
        # Each scene gets its own instances of engine systems.
        self.input = InputManager()
        self.camera = Camera()
        self.assets = game.assets

    def create(self):
        """Called once when the scene is started."""
        pass

    def resume(self):
        """
        NEW: Called when a scene becomes active again after a scene on top of it
        is popped (e.g., returning from a menu or shop).
        """
        pass

    def update(self, dt: float) -> Optional[str]:
        """
        Called every logic frame. 'dt' is the fixed timestep.
        Can return a string signal like "CHANGE_SCENE" to the game loop.
        """
        pass

    def draw(self, frame_time_ms: int):
        """Called every render frame to draw the scene."""
        pass

    def destroy(self):
        """Called when the scene is being shut down, for cleanup."""
        pass
