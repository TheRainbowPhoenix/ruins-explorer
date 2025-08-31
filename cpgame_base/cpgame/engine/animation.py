# engine/animation.py
# Manages animation frames and state.
try:
    from typing import Optional, List, Dict, Any, Tuple, Union
except:
    pass

class AnimationFrame:
    """Represents a single frame of an animation, loaded from asset data."""
    # def __init__(self, img, imgH, x, y, w, h, cx, cy, duration):
    def __init__(self, img: Any, src_x: int, src_y: int, width: int, height: int, pivot_x: int, pivot_y: int, duration: int):
        # Source image and position
        self.img = img      # Source image containing the frame
        self.src_x = src_x  # X position of frame in source image
        self.src_y = src_y  # Y position of frame in source image
        
        # Frame dimensions
        self.width = width    # Width of the frame
        self.height = height  # Height of the frame
        
        # Drawing offset (pivot point)
        self.pivot_x = pivot_x  # Offset from top-left for drawing position
        self.pivot_y = pivot_y  # Offset from top-left for drawing position
        
        # Timing
        self.duration = duration  # How long to display this frame (milliseconds)


class Animation:
    """A complete animation with frames and playback properties (Phaser-inspired)."""
    def __init__(self, key: str, frames: List[AnimationFrame], frame_rate: float = 24.0, repeat: int = -1):
        self.key = key
        self.frames = frames
        self.frame_rate = frame_rate
        self.repeat = repeat  # -1 for infinite
        self.ms_per_frame = 1000.0 / frame_rate if frame_rate > 0 else 0
        self.duration = len(frames) * self.ms_per_frame
        self.yoyo = False
        self.paused = False
        self.hide_on_complete = False
        self.show_on_start = True

class AnimationVariantManager:
    """Manages different variants of animations (flipped, rotated, etc.)"""
    def __init__(self):
        self.variants: Dict[str, Animation] = {}
    
    def register_variant(self, base_name: str, variant_name: str, animation: Animation):
        """Register a variant of an animation."""
        key = f"{base_name}:{variant_name}"
        self.variants[key] = animation
    
    def get_variant(self, base_name: str, variant_name: str) -> Optional[Animation]:
        """Get a specific variant of an animation."""
        key = f"{base_name}:{variant_name}"
        return self.variants.get(key)
    
    def get_appropriate_variant(self, base_name: str, **states) -> Optional[Animation]:
        """Get the appropriate variant based on current states."""
        # For now, handle flipped state
        if states.get('flipped', False):
            flipped_anim = self.get_variant(base_name, 'flipped')
            if flipped_anim:
                return flipped_anim
        # Return base animation
        return self.get_variant(base_name, 'normal') or self.variants.get(f"{base_name}:normal")


class AnimationState:
    """Manages the state of an active animation for a game object."""
    def __init__(self):
        self.animation: Optional[Animation] = None
        self.frames: Optional[List[AnimationFrame]] = None
        self.index: int = -1
        self.elapsed: float = 0.0
        self.repeat_count: int = 0
        self.forward: bool = True  # For yoyo support
        self.base_name: str = ""  # Store the base animation name
        self.variant_manager: Optional[AnimationVariantManager] = None

    def set_base_animation(self, base_name: str, variant_manager: AnimationVariantManager):
        """Set base animation name and variant manager for dynamic variant selection."""
        self.base_name = base_name
        self.variant_manager = variant_manager
        # Initially set to normal variant
        self._update_variant(**{})

    def _update_variant(self, **states):
        """Update to the appropriate variant based on current states."""
        if self.variant_manager and self.base_name:
            new_anim = self.variant_manager.get_appropriate_variant(self.base_name, **states)
            if new_anim and new_anim != self.animation:
                self.set_animation(new_anim)

    def update_variant_states(self, **states):
        """Update variant based on new states (like flipped=True)."""
        self._update_variant(**states)

    def set_animation(self, animation: Animation):
        """Sets a new animation and resets its state."""
        self.animation = animation
        self.frames = animation.frames
        self.index = 0 if animation.frames else -1
        self.elapsed = 0.0
        self.repeat_count = 0
        self.forward = True

    def set_frames(self, frames: List[AnimationFrame]):
        """Sets new frames directly and resets state."""
        self.animation = None
        self.frames = frames
        self.index = 0 if frames else -1
        self.elapsed = 0.0
        self.repeat_count = 0
        self.forward = True

    def set(self, frames: List[AnimationFrame]):
        """Sets a new animation and resets its state."""
        self.frames, self.index, self.elapsed = frames, 0, 0.0

    def update(self, dt: float) -> bool:
        """
        Advances the animation by a time delta.
        Returns True if the animation has just looped.
        """
        if self.index < 0 or not self.frames or (self.animation and self.animation.paused):
            return False
        self.elapsed += dt
        
        # Get current frame duration
        current_frame = self.frames[self.index]
        frame_duration = current_frame.duration / 1000.0  # Convert ms to seconds
        
        if self.elapsed >= frame_duration:
            self.elapsed = 0
            just_looped = False
            
            if self.animation:
                # Handle yoyo
                if self.animation.yoyo:
                    if self.forward:
                        if self.index < len(self.frames) - 1:
                            self.index += 1
                        else:
                            if self.animation.repeat == -1 or self.repeat_count < self.animation.repeat:
                                self.forward = False
                                self.index -= 1
                                self.repeat_count += 1
                                just_looped = True
                            elif self.animation.hide_on_complete:
                                # TODO: Hide the game object
                                pass
                    else:
                        if self.index > 0:
                            self.index -= 1
                        else:
                            if self.animation.repeat == -1 or self.repeat_count < self.animation.repeat:
                                self.forward = True
                                self.index += 1
                                self.repeat_count += 1
                                just_looped = True
                            elif self.animation.hide_on_complete:
                                # TODO: Hide the game object
                                pass
                else:
                    # Normal playback
                    if self.index < len(self.frames) - 1:
                        self.index += 1
                    else:
                        if self.animation.repeat == -1 or self.repeat_count < self.animation.repeat:
                            self.index = 0
                            self.repeat_count += 1
                            just_looped = True
                        elif self.animation.hide_on_complete:
                            # TODO: Hide the game object
                            pass
            else:
                # No animation object, just cycle through frames
                if self.index < len(self.frames) - 1:
                    self.index += 1
                else:
                    self.index = 0
                    just_looped = True
                    
            return just_looped
        return False

    def get_current_frame(self) -> Optional[AnimationFrame]:
        """Returns the current frame of the animation."""
        if self.frames and 0 <= self.index < len(self.frames):
            return self.frames[self.index]
        return None

    def is_animation_finished(self) -> bool:
        """Checks if the animation has completed."""
        if not self.frames:
            return True
        if not self.animation:
            return self.index == len(self.frames) - 1
        if self.animation.repeat == -1:
            return False
        return (self.repeat_count >= self.animation.repeat and 
                self.index == len(self.frames) - 1)