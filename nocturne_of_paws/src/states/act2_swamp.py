"""
Act 2 — The Sunken Kingdom of the Oracles.

A bioluminescent swamp beneath a star-lit sky. Giant Lilypad Oracle frogs
in cracked porcelain crowns drift on black water; a great Weeping Willow
glows at the heart of the mire. Reuses the Weather system (teal fireflies as
bioluminescence, rolling fog, no rose petals) for the living-world feel.
"""

import math
import pygame
from src.states.base_state import BaseState
from src.core.weather import Weather

NATIVE_W, NATIVE_H = 320, 180

OBSIDIAN     = (10,   8,  14)
SWAMP_GREEN  = (16,  40,  34)
DEEP_WATER   = (8,   18,  24)
MIST_BLUE    = (40,  80,  90)
GLOW_TEAL    = (70, 210, 170)
WILLOW_GLOW  = (120, 220, 180)
PORCELAIN    = (220, 215, 225)
CROWN_GOLD   = (210, 170, 60)


class Act2SwampState(BaseState):
    def __init__(self, engine):
        super().__init__(engine)
        self._timer = 0.0
        self.weather = Weather(NATIVE_W, NATIVE_H)
        self.weather.petals = False          # no roses in the swamp
        self.weather.stars  = True           # star-lit sky
        # Tint fireflies toward bioluminescent teal by overriding their colour use
        # (handled in draw via our own glow motes layered atop weather).
        self._oracles = [
            {"x": 70,  "y": 150, "scale": 1.0, "phase": 0.0},
            {"x": 180, "y": 158, "scale": 1.3, "phase": 1.7},
            {"x": 265, "y": 150, "scale": 0.9, "phase": 3.1},
        ]

    def on_enter(self):
        pass

    def update(self, dt):
        self._timer += dt
        self.weather.update(dt)
        if self.input.pressed("pause"):
            self.state_mgr.pop()

    # ── Draw ──────────────────────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface):
        w, h = surface.get_size()
        self._draw_sky(surface, w, h)
        self._draw_willow(surface, w, h)
        self._draw_water(surface, w, h)
        self._draw_oracles(surface)
        self.weather.draw(surface)
        self._draw_bioluminescence(surface, w, h)

    def draw_overlay(self, surface):
        w, h = surface.get_size()
        font = pygame.font.SysFont("courier", 7, bold=True)
        msg = font.render("ACT II — The Sunken Kingdom of the Oracles", True, GLOW_TEAL)
        surface.blit(msg, (w // 2 - msg.get_width() // 2, 10))

    # ── Layers ────────────────────────────────────────────────────────────────

    def _draw_sky(self, surface, w, h):
        for y in range(h):
            t = y / h
            r = int(OBSIDIAN[0] * (1 - t) + SWAMP_GREEN[0] * t)
            g = int(OBSIDIAN[1] * (1 - t) + SWAMP_GREEN[1] * t)
            b = int(OBSIDIAN[2] * (1 - t) + SWAMP_GREEN[2] * t)
            pygame.draw.line(surface, (r, g, b), (0, y), (w, y))

    def _draw_willow(self, surface, w, h):
        # Trunk + glowing drooping fronds at swamp centre
        tx = w // 2
        pygame.draw.rect(surface, (30, 22, 26), (tx - 4, h - 80, 8, 50))
        for i in range(-5, 6):
            sway = math.sin(self._timer * 1.2 + i) * 3
            fx = tx + i * 9
            for seg in range(6):
                fy = h - 90 + seg * 7
                a = 90 - seg * 12
                col = (WILLOW_GLOW[0], WILLOW_GLOW[1], WILLOW_GLOW[2])
                surf = pygame.Surface((3, 6), pygame.SRCALPHA)
                surf.fill((*col, max(20, a)))
                surface.blit(surf, (int(fx + sway * (seg / 6)), fy))

    def _draw_water(self, surface, w, h):
        water_y = h - 30
        pygame.draw.rect(surface, DEEP_WATER, (0, water_y, w, 30))
        # Shimmering ripples
        for i in range(0, w, 6):
            rip = math.sin(self._timer * 2 + i * 0.3) * 1.5
            shade = int(20 + 15 * (0.5 + 0.5 * math.sin(self._timer + i)))
            surface.set_at((i, int(water_y + 4 + rip)), (shade, shade + 30, shade + 35))

    def _draw_oracles(self, surface):
        """Giant frogs in cracked porcelain crowns drifting on the water."""
        for o in self._oracles:
            bob = math.sin(self._timer * 1.1 + o["phase"]) * 2
            x, y = int(o["x"]), int(o["y"] + bob)
            s = o["scale"]
            bw, bh = int(22 * s), int(12 * s)
            # Body
            pygame.draw.ellipse(surface, (28, 70, 48), (x - bw // 2, y, bw, bh))
            pygame.draw.ellipse(surface, (40, 95, 62), (x - bw // 2, y, bw, bh), 1)
            # Eyes
            for ex in (-bw // 4, bw // 4):
                pygame.draw.circle(surface, (20, 50, 34), (x + ex, y), 3)
                pygame.draw.circle(surface, GLOW_TEAL, (x + ex, y - 1), 1)
            # Cracked porcelain crown
            cw = bw // 2
            pygame.draw.rect(surface, PORCELAIN, (x - cw // 2, y - 6, cw, 4))
            for k in range(3):
                kx = x - cw // 2 + k * (cw // 2)
                pygame.draw.polygon(surface, CROWN_GOLD,
                                    [(kx, y - 6), (kx + 2, y - 10), (kx + 4, y - 6)])
            # ripple ring beneath
            pygame.draw.ellipse(surface, (30, 60, 60),
                                (x - bw // 2 - 3, y + bh - 2, bw + 6, 4), 1)

    def _draw_bioluminescence(self, surface, w, h):
        # Teal glow motes rising from the water
        for i in range(10):
            mx = int((i * 37 + self._timer * 10) % w)
            my = int(h - 20 - ((self._timer * 18 + i * 30) % (h * 0.6)))
            glow = 0.5 + 0.5 * math.sin(self._timer * 2 + i)
            halo = pygame.Surface((5, 5), pygame.SRCALPHA)
            pygame.draw.circle(halo, (*GLOW_TEAL, int(60 * glow)), (2, 2), 2)
            surface.blit(halo, (mx, my))
            surface.set_at((mx + 2, my + 2), GLOW_TEAL)
