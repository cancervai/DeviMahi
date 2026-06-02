"""
Act 2 — The Bioluminescent Swamp: atmospheric exploration with fog and glowing flora.
Placeholder state — full implementation follows in a later sprint.
"""

import math
import pygame
from src.states.base_state import BaseState

OBSIDIAN     = (10,  8, 14)
SWAMP_GREEN  = (20, 55, 30)
MIST_BLUE    = (40, 80, 90)
GLOW_TEAL    = (60, 200, 160)


class Act2SwampState(BaseState):
    def __init__(self, engine):
        super().__init__(engine)
        self._timer = 0.0

    def on_enter(self):
        pass

    def update(self, dt):
        self._timer += dt
        if self.input.pressed("pause"):
            self.state_mgr.pop()

    def draw(self, surface: pygame.Surface):
        w, h = surface.get_size()
        surface.fill(OBSIDIAN)

        # Misty horizon
        for y in range(h // 2, h):
            t = (y - h // 2) / (h // 2)
            r = int(OBSIDIAN[0] * (1 - t) + SWAMP_GREEN[0] * t)
            g = int(OBSIDIAN[1] * (1 - t) + SWAMP_GREEN[1] * t)
            b = int(OBSIDIAN[2] * (1 - t) + SWAMP_GREEN[2] * t)
            pygame.draw.line(surface, (r, g, b), (0, y), (w, y))

        # Floating bioluminescent orbs (placeholder flora)
        for i in range(8):
            ox = int((i * 42 + self._timer * 8) % w)
            oy = int(h * 0.6 + math.sin(self._timer * 1.5 + i) * 10)
            pygame.draw.circle(surface, GLOW_TEAL, (ox, oy), 2)

        font = pygame.font.SysFont("courier", 7)
        msg = font.render("Act II: The Bioluminescent Swamp  [coming soon]", True, GLOW_TEAL)
        surface.blit(msg, (w // 2 - msg.get_width() // 2, h // 2 - 10))
