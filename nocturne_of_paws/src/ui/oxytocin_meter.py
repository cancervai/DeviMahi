"""
Oxytocin (Bond) Meter — displays the emotional bond between Masum and Mahi.

Rendered as a small glowing heart bar in the top-right corner.
Value range: 0–100. Pulses when increasing; dims when decreasing.
"""

import math
import pygame

METER_MAX    = 100
BAR_W        = 40
BAR_H        = 5
HEART_COL    = (200,  50,  80)
HEART_GLOW   = (240, 100, 120)
EMPTY_COL    = (60,   20,  25)
BORDER_COL   = (120,  30,  40)
LABEL_COL    = (180, 140, 150)


class OxytocinMeter:
    def __init__(self, initial: int = 0):
        self._value  = float(max(0, min(METER_MAX, initial)))
        self._target = self._value
        self._pulse  = 0.0
        self._timer  = 0.0

    # ── API ───────────────────────────────────────────────────────────────────

    def increase(self, amount: float):
        self._target = min(METER_MAX, self._target + amount)
        self._pulse  = 1.0

    def decrease(self, amount: float):
        self._target = max(0, self._target - amount)

    @property
    def value(self) -> float:
        return self._value

    # ── Update ────────────────────────────────────────────────────────────────

    def update(self, dt: float):
        self._timer  += dt
        self._pulse   = max(0.0, self._pulse - dt * 2)
        self._value  += (self._target - self._value) * min(1.0, dt * 4)

    # ── Draw ──────────────────────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface):
        w, _ = surface.get_size()
        x    = w - BAR_W - 6
        y    = 4

        font = pygame.font.SysFont("courier", 5)

        # Label
        lbl = font.render("BOND", True, LABEL_COL)
        surface.blit(lbl, (x, y))

        bar_y = y + 7

        # Background bar
        pygame.draw.rect(surface, EMPTY_COL, (x, bar_y, BAR_W, BAR_H))

        # Filled portion
        fill = int(BAR_W * (self._value / METER_MAX))
        if fill > 0:
            pulse = 0.8 + 0.2 * math.sin(self._timer * 6) * self._pulse
            r = int(min(255, HEART_COL[0] * pulse + HEART_GLOW[0] * self._pulse * 0.3))
            g = int(HEART_COL[1] * pulse)
            b = int(HEART_COL[2] * pulse)
            pygame.draw.rect(surface, (r, g, b), (x, bar_y, fill, BAR_H))

        # Border
        pygame.draw.rect(surface, BORDER_COL, (x, bar_y, BAR_W, BAR_H), 1)

        # Heart icon (3×3 pixel art)
        hx, hy = x - 6, bar_y - 1
        heart_pixels = [
            (0, 0), (1, 0), (3, 0), (4, 0),
            (0, 1), (1, 1), (2, 1), (3, 1), (4, 1),
            (1, 2), (2, 2), (3, 2),
            (2, 3),
        ]
        col = HEART_GLOW if self._pulse > 0 else HEART_COL
        for px, py in heart_pixels:
            if hx + px < w and hy + py >= 0:
                surface.set_at((hx + px, hy + py), col)
