"""
NpcFrog — ambient gothic swamp frog NPCs.

Patrol a small range, croak when Masum approaches, and trigger lore dialogue.
"""

import math
import pygame

FROG_GREEN  = (40, 100, 50)
FROG_BELLY  = (80, 160, 70)
FROG_EYE    = (200, 200, 30)
PATROL_DIST = 24
WALK_SPEED  = 18.0


class NpcFrog:
    def __init__(self, x: float, y: float):
        self.rect     = pygame.Rect(int(x), int(y), 8, 6)
        self._origin  = float(x)
        self._fx      = float(x)
        self._dir     = 1
        self._anim_t  = 0.0
        self._hop     = 0.0    # vertical hop offset
        self._hop_vy  = 0.0
        self._hop_timer = 0.0
        self._sprite  = self._build_sprite()

    def _build_sprite(self) -> pygame.Surface:
        surf = pygame.Surface((8, 6), pygame.SRCALPHA)
        # Body
        for row, line in enumerate([
            " GGGG  ",
            "GGGGGGG",
            "GBBBBGG",
            " GGGG  ",
            "G    G ",
            "G    G ",
        ]):
            for col, ch in enumerate(line):
                if ch == "G":
                    surf.set_at((col, row), FROG_GREEN)
                elif ch == "B":
                    surf.set_at((col, row), FROG_BELLY)
        surf.set_at((1, 0), FROG_EYE)
        surf.set_at((5, 0), FROG_EYE)
        return surf

    def update(self, dt: float):
        self._anim_t   += dt
        self._hop_timer += dt

        # Periodic hop
        if self._hop_timer > 1.2 and self._hop == 0:
            self._hop_timer = 0
            self._hop_vy    = -30.0

        if self._hop_vy != 0 or self._hop != 0:
            self._hop_vy += 120 * dt
            self._hop    += self._hop_vy * dt
            if self._hop >= 0:
                self._hop    = 0
                self._hop_vy = 0

        # Patrol
        self._fx += self._dir * WALK_SPEED * dt
        if abs(self._fx - self._origin) > PATROL_DIST:
            self._dir *= -1

        self.rect.x = int(self._fx)
        self.rect.y = self.rect.y + int(self._hop)

    def draw(self, surface: pygame.Surface, camera):
        sx, sy = camera.world_to_screen(self.rect.x, self.rect.y)
        sprite = self._sprite
        if self._dir == -1:
            sprite = pygame.transform.flip(sprite, True, False)
        surface.blit(sprite, (sx, sy))
