# cpgame/game_objects/timer.py
# This class handles the game timer.

import math

class GameTimer:
    """
    Handles a countdown timer. The instance is updated by the main game loop
    with a delta time (dt) to avoid performance issues.
    """
    def __init__(self):
        self._count = 0.0  # Use a float for accurate dt accumulation
        self._working = False
        self._total_seconds = 0.0

    def is_working(self) -> bool:
        """Returns True if the timer is running."""
        return self._working

    def start(self, seconds: int):
        """Starts or restarts the timer with a given duration in seconds."""
        self._count = float(seconds)
        self._working = True

    def stop(self):
        """Stops the timer."""
        self._working = False

    def update(self, dt: float):
        """Updates the timer countdown. Called once per frame."""
        self._total_seconds += dt
        if self._working and self._count > 0:
            self._count -= dt
            if self._count <= 0:
                self._count = 0
                self.on_expire()

    @property
    def total_play_time(self) -> int:
        """Returns the total elapsed game time in seconds."""
        return int(math.ceil(self._total_seconds))

    @property
    def sec(self) -> int:
        """Gets the remaining whole seconds on the timer."""
        return int(math.ceil(self._count))

    def on_expire(self):
        """Called when the timer reaches zero."""
        # In a full game, this might trigger a common event or abort a battle.
        # For now, we can just log it.
        from cpgame.engine.logger import log
        log("Timer expired!")
        self._working = False
    