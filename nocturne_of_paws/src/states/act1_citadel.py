"""
Act 1 — The Obsidian Citadel: 2D side-scrolling exploration.
Masum (player) explores gothic architecture while Mahi follows as companion.
"""

import pygame
from src.states.base_state import BaseState
from src.core.camera import Camera
from src.entities.player_masum import PlayerMasum
from src.entities.companion_mahi import CompanionMahi
from src.entities.npc_frogs import NpcFrog
from src.ui.dialogue_system import DialogueSystem
from src.ui.oxytocin_meter import OxytocinMeter

NATIVE_W, NATIVE_H = 320, 180
WORLD_W,  WORLD_H  = 1280, 360

DARK_MAROON  = (42,   6,  12)
OBSIDIAN     = (10,   8,  14)
DEEP_CRIMSON = (90,  10,  20)
STONE_GREY   = (55,  48,  60)
CANDLE_GOLD  = (220, 160,  40)


class Act1CitadelState(BaseState):
    def __init__(self, engine):
        super().__init__(engine)
        self.camera    = Camera(NATIVE_W, NATIVE_H, WORLD_W, WORLD_H)
        self.player    = PlayerMasum(64, WORLD_H - 64)
        self.companion = CompanionMahi(96, WORLD_H - 64)
        self.frogs     = [NpcFrog(320 + i * 128, WORLD_H - 40) for i in range(4)]
        self.dialogue  = DialogueSystem()
        self.oxytocin  = OxytocinMeter(initial=20)
        self._floors   = self._build_floors()
        self._timer    = 0.0

    # ── World geometry ────────────────────────────────────────────────────────

    def _build_floors(self):
        """Simple platform layout for Act 1."""
        floors = [
            pygame.Rect(0,       WORLD_H - 16, WORLD_W, 16),   # ground
            pygame.Rect(200,     WORLD_H - 56,  96, 8),
            pygame.Rect(400,     WORLD_H - 80,  64, 8),
            pygame.Rect(560,     WORLD_H - 56, 112, 8),
            pygame.Rect(760,     WORLD_H - 96,  80, 8),
            pygame.Rect(920,     WORLD_H - 64, 160, 8),
            pygame.Rect(1120,    WORLD_H - 80,  96, 8),
        ]
        return floors

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def on_enter(self):
        # Trigger opening dialogue
        self.dialogue.queue([
            ("Masum", "...The Citadel smells of old roses and iron."),
            ("Mahi",  "Stay close. The corridors remember those who wander."),
        ])

    # ── Update ────────────────────────────────────────────────────────────────

    def update(self, dt):
        self._timer += dt

        self.player.update(dt, self.input, self._floors)
        self.companion.update(dt, self.player.rect)
        for frog in self.frogs:
            frog.update(dt)
        self.dialogue.update(dt, self.input)
        self.camera.update(self.player.rect, dt)

        # Pause-to-menu
        if self.input.pressed("pause"):
            from src.states.menu import MenuState
            self.state_mgr.push(MenuState(self.engine))

    # ── Draw ──────────────────────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface):
        surface.fill(OBSIDIAN)
        self._draw_background(surface)
        self._draw_floors(surface)
        for frog in self.frogs:
            frog.draw(surface, self.camera)
        self.companion.draw(surface, self.camera)
        self.player.draw(surface, self.camera)
        self.dialogue.draw(surface)
        self.oxytocin.draw(surface)

    def _draw_background(self, surface):
        # Parallax gothic sky — three depth layers
        w, h = surface.get_size()
        ox, _ = self.camera.offset

        # Far layer: gothic arched windows silhouette
        for i in range(6):
            wx = i * 220 - (ox * 0.2 % 220)
            pygame.draw.rect(surface, (25, 12, 20), (int(wx), 10, 40, 60))
            pygame.draw.arc(surface, (35, 16, 28),
                            pygame.Rect(int(wx), 10, 40, 30), 0, 3.14159, 2)

        # Mid layer: distant tower spires
        for i in range(8):
            sx = int(i * 160 - (ox * 0.5 % 160))
            tower_h = 40 + (i % 3) * 15
            pygame.draw.rect(surface, STONE_GREY, (sx, h - tower_h - 16, 10, tower_h))
            # Spire tip
            pygame.draw.polygon(surface, (45, 38, 50),
                                [(sx, h - tower_h - 16),
                                 (sx + 5, h - tower_h - 28),
                                 (sx + 10, h - tower_h - 16)])

        # Candle glow blobs in windows
        import math
        for i in range(4):
            cx = int(i * 300 + 80 - (ox * 0.3 % 300))
            cy = 30 + (i % 2) * 20
            flicker = math.sin(self._timer * 5 + i * 1.3) * 2
            r = int(3 + flicker)
            pygame.draw.circle(surface, CANDLE_GOLD, (cx % w, cy), max(1, r))

    def _draw_floors(self, surface):
        for rect in self._floors:
            screen_rect = self.camera.apply(rect)
            pygame.draw.rect(surface, STONE_GREY, screen_rect)
            # Top edge highlight
            pygame.draw.line(surface, (80, 65, 75),
                             screen_rect.topleft, screen_rect.topright)
