"""
Main Menu state — gothic title screen with flickering candle effect.
"""

import math
import pygame
from src.states.base_state import BaseState

# Palette
DARK_MAROON  = (42,  6, 12)
DEEP_CRIMSON = (90, 10, 20)
CANDLE_GOLD  = (220, 160, 40)
GHOST_WHITE  = (230, 225, 235)
DIM_GREY     = (80,  70,  80)
OBSIDIAN     = (10,   8,  14)


class MenuState(BaseState):
    def __init__(self, engine):
        super().__init__(engine)
        self._timer    = 0.0
        self._selected = 0
        self._options  = ["Begin the Nocturne", "Load Save", "Settings", "Quit"]

    def on_enter(self):
        self._selected = 0

    # ── Update ────────────────────────────────────────────────────────────────

    def update(self, dt):
        self._timer += dt

        if self.input.pressed("move_up"):
            self._selected = (self._selected - 1) % len(self._options)
        if self.input.pressed("move_down"):
            self._selected = (self._selected + 1) % len(self._options)

        if self.input.pressed("interact"):
            self._activate(self._selected)

    def _activate(self, idx):
        label = self._options[idx]
        if label == "Begin the Nocturne":
            from src.states.act1_citadel import Act1CitadelState
            self.state_mgr.replace(Act1CitadelState(self.engine))
        elif label == "Quit":
            self.engine.running = False

    # ── Draw ──────────────────────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface):
        w, h = surface.get_size()

        # Animated gothic vignette
        self._draw_background(surface, w, h)
        self._draw_candles(surface, w, h)
        self._draw_title(surface, w, h)
        self._draw_menu(surface, w, h)
        self._draw_tagline(surface, w, h)

    def _draw_background(self, surface, w, h):
        surface.fill(DARK_MAROON)
        # Subtle gradient overlay — horizontal dark bands
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        for i in range(h):
            alpha = int(80 * (i / h))
            pygame.draw.line(overlay, (0, 0, 0, alpha), (0, i), (w, i))
        surface.blit(overlay, (0, 0))

    def _draw_candles(self, surface, w, h):
        positions = [(18, h - 28), (w - 22, h - 28), (w // 2 - 60, h - 22), (w // 2 + 56, h - 22)]
        for cx, cy in positions:
            flicker = math.sin(self._timer * 6.0 + cx) * 2
            # Candle body
            pygame.draw.rect(surface, (160, 100, 30), (cx - 2, cy - 8, 4, 10))
            # Flame glow
            flame_r = int(4 + flicker)
            glow_col = (min(255, CANDLE_GOLD[0] + 20), CANDLE_GOLD[1], CANDLE_GOLD[2] // 4)
            pygame.draw.circle(surface, glow_col, (cx, cy - 10 + int(flicker * 0.5)), flame_r)
            pygame.draw.circle(surface, GHOST_WHITE, (cx, cy - 12 + int(flicker * 0.5)), 1)

    def _draw_title(self, surface, w, h):
        font_lg = pygame.font.SysFont("courier", 14, bold=True)
        font_sm = pygame.font.SysFont("courier", 6)

        pulse = 0.85 + 0.15 * math.sin(self._timer * 1.4)
        r = int(CANDLE_GOLD[0] * pulse)
        g = int(CANDLE_GOLD[1] * pulse)
        b = int(CANDLE_GOLD[2] * pulse * 0.3)

        title_surf = font_lg.render("NOCTURNE  OF  PAWS", True, (r, g, b))
        surface.blit(title_surf, (w // 2 - title_surf.get_width() // 2, 22))

        sub_surf = font_sm.render("~ A Gothic Romance of Masum & Mahi ~", True, DIM_GREY)
        surface.blit(sub_surf, (w // 2 - sub_surf.get_width() // 2, 42))

    def _draw_menu(self, surface, w, h):
        font = pygame.font.SysFont("courier", 8, bold=True)
        start_y = 72

        for i, option in enumerate(self._options):
            selected = (i == self._selected)
            pulse = 0.7 + 0.3 * math.sin(self._timer * 3.0) if selected else 0.0

            if selected:
                r = int(CANDLE_GOLD[0] * (0.85 + pulse * 0.15))
                color = (r, CANDLE_GOLD[1], CANDLE_GOLD[2] // 3)
                prefix = "> "
            else:
                color = DIM_GREY
                prefix = "  "

            text = font.render(prefix + option, True, color)
            surface.blit(text, (w // 2 - text.get_width() // 2, start_y + i * 18))

    def _draw_tagline(self, surface, w, h):
        font = pygame.font.SysFont("courier", 5)
        alpha = int(128 + 127 * math.sin(self._timer * 0.8))
        tag = font.render("[ ENTER ] to select", True, (alpha // 2, alpha // 3, alpha // 2))
        surface.blit(tag, (w // 2 - tag.get_width() // 2, h - 14))
