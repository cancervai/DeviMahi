"""
Smooth-follow camera for 2D side-scrolling.

The camera tracks a target rect and lerps toward it each frame.
world_to_screen() converts world-space coordinates to canvas-space for rendering.
"""

import pygame


class Camera:
    def __init__(self, native_w: int, native_h: int, world_w: int, world_h: int,
                 lerp: float = 8.0):
        self.native_w = native_w
        self.native_h = native_h
        self.world_w  = world_w
        self.world_h  = world_h
        self.lerp     = lerp             # Higher = snappier follow

        # Camera top-left in world space (float for smooth movement)
        self._x = 0.0
        self._y = 0.0

    # ── Update ────────────────────────────────────────────────────────────────

    def update(self, target_rect: pygame.Rect, dt: float):
        """Smoothly centre the camera on target_rect."""
        target_x = target_rect.centerx - self.native_w // 2
        target_y = target_rect.centery - self.native_h // 2

        t = min(1.0, self.lerp * dt)
        self._x += (target_x - self._x) * t
        self._y += (target_y - self._y) * t

        # Clamp to world bounds
        self._x = max(0, min(self._x, self.world_w  - self.native_w))
        self._y = max(0, min(self._y, self.world_h  - self.native_h))

    # ── Coordinate conversion ─────────────────────────────────────────────────

    def world_to_screen(self, world_x: float, world_y: float) -> tuple[int, int]:
        return int(world_x - self._x), int(world_y - self._y)

    def apply(self, rect: pygame.Rect) -> pygame.Rect:
        """Return a new Rect offset by the camera."""
        return rect.move(-int(self._x), -int(self._y))

    @property
    def offset(self) -> tuple[int, int]:
        return int(self._x), int(self._y)
