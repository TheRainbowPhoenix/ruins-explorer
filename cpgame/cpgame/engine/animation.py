# engine/animation.py
# Manages animation frames and state.
try:
    from typing import Optional, List
except:
    pass

class AnimationFrame:
    """Represents a single frame of an animation, loaded from asset data."""
    def __init__(self, img, imgH, x, y, w, h, cx, cy, duration):
        self.img, self.imgH = img, imgH
        self.x, self.y, self.w, self.h = x, y, w, h
        self.cx, self.cy = cx, cy
        self.duration = duration

class AnimationState:
    """Manages the state of an active animation for a game object."""
    def __init__(self):
        self.frames: Optional[List[AnimationFrame]] = None
        self.index: int = -1
        self.elapsed: float = 0.0

    def set(self, frames: List[AnimationFrame]):
        """Sets a new animation and resets its state."""
        self.frames, self.index, self.elapsed = frames, 0, 0.0

    def update(self, dt: float) -> bool:
        """
        Advances the animation by a time delta.
        Returns True if the animation has just looped.
        """
        if self.index < 0 or not self.frames: return False
        self.elapsed += dt
        if self.elapsed * 1000 >= self.frames[self.index].duration:
            self.elapsed = 0
            self.index = (self.index + 1) % len(self.frames)
            return self.index == 0
        return False

    def get_current_frame(self) -> Optional[AnimationFrame]:
        """Returns the current frame of the animation."""
        if self.frames and self.index >= 0:
            return self.frames[self.index]
        return None

    def is_animation_finished(self) -> bool:
        """Checks if the animation has completed a full cycle."""
        return self.index == len(self.frames) - 1 if self.frames else False
