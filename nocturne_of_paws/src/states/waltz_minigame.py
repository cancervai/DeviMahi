"""
Waltz Minigame — rhythm-based partner dance between Masum and Mahi.
Beat markers scroll in from the right; press the correct direction key on beat.
Placeholder structure — full rhythm engine implemented in a later sprint.
"""

import math
import pygame
from src.states.base_state import BaseState

OBSIDIAN    = (10,   8,  14)
DARK_MAROON = (42,   6,  12)
CANDLE_GOLD = (220, 160,  40)
ROSE_PINK   = (200,  80, 110)
GHOST_WHITE = (230, 225, 235)

BPM          = 120
BEAT_INTERVAL = 60.0 / BPM


class WaltzMinigameState(BaseState):
    def __init__(self, engine):
        super().__init__(engine)
        self._timer      = 0.0
        self._beat_timer = 0.0
        self._score      = 0
        self._combo      = 0
        self._markers    = []   # list of (x, lane, age)
        self._hit_flash  = 0.0

    def on_enter(self):
        self._score = 0
        self._combo = 0

    def update(self, dt):
        self._timer      += dt
        self._beat_timer += dt
        self._hit_flash   = max(0.0, self._hit_flash - dt * 4)

        # Spawn a beat marker every beat
        if self._beat_timer >= BEAT_INTERVAL:
            self._beat_timer -= BEAT_INTERVAL
            lane = int(self._timer * 3) % 4   # cycle through 4 lanes
            self._markers.append([320, lane, 0.0])

        # Scroll markers left
        SPEED = 80
        for m in self._markers:
            m[0] -= SPEED * dt
            m[2] += dt
        self._markers = [m for m in self._markers if m[0] > -10]

        # Input: check if any marker is in the hit zone (x ~20)
        actions = ["move_left", "move_right", "move_up", "move_down"]
        for i, action in enumerate(actions):
            if self.input.pressed(action):
                for m in self._markers:
                    if m[1] == i and abs(m[0] - 20) < 12:
                        self._score += 10 * (1 + self._combo)
                        self._combo += 1
                        self._hit_flash = 1.0
                        self._markers.remove(m)
                        break
                else:
                    self._combo = 0

        if self.input.pressed("pause"):
            self.state_mgr.pop()

    def draw(self, surface: pygame.Surface):
        w, h = surface.get_size()
        surface.fill(DARK_MAROON)

        self._draw_dance_floor(surface, w, h)
        self._draw_markers(surface, w, h)
        self._draw_hud(surface, w, h)

    def _draw_dance_floor(self, surface, w, h):
        lane_h = 20
        lane_y = h // 2 - 40
        labels = ["←", "→", "↑", "↓"]
        for i in range(4):
            y = lane_y + i * (lane_h + 4)
            pygame.draw.rect(surface, (30, 10, 18), (10, y, w - 20, lane_h))
            pygame.draw.rect(surface, (60, 20, 35), (10, y, w - 20, lane_h), 1)
            # Hit zone marker
            glow = int(180 + 75 * math.sin(self._timer * 4 + i))
            pygame.draw.rect(surface, (glow // 2, glow // 4, 20), (12, y + 1, 18, lane_h - 2))
            font = pygame.font.SysFont("courier", 7)
            lbl = font.render(labels[i], True, CANDLE_GOLD)
            surface.blit(lbl, (14, y + lane_h // 2 - lbl.get_height() // 2))

    def _draw_markers(self, surface, w, h):
        lane_h = 20
        lane_y = h // 2 - 40
        for mx, lane, age in self._markers:
            y = lane_y + lane * (lane_h + 4)
            t = min(1.0, age * 2)
            r = int(ROSE_PINK[0] * t + CANDLE_GOLD[0] * (1 - t))
            g = int(ROSE_PINK[1] * t + CANDLE_GOLD[1] * (1 - t))
            b = int(ROSE_PINK[2] * t + CANDLE_GOLD[2] * (1 - t))
            pygame.draw.rect(surface, (r, g, b), (int(mx), y + 2, 14, lane_h - 4), border_radius=3)

    def _draw_hud(self, surface, w, h):
        font = pygame.font.SysFont("courier", 8, bold=True)
        score_txt = font.render(f"Score: {self._score}   Combo: x{self._combo}", True, GHOST_WHITE)
        surface.blit(score_txt, (w // 2 - score_txt.get_width() // 2, 8))

        if self._hit_flash > 0:
            flash_alpha = int(self._hit_flash * 180)
            flash = pygame.Surface((w, h), pygame.SRCALPHA)
            flash.fill((220, 160, 40, flash_alpha))
            surface.blit(flash, (0, 0))
