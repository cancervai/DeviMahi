"""
Core game engine: pixel-perfect window, game loop, delta-time, scaling.

Internal canvas: 320x180 (native 8-bit resolution).
Displayed surface: largest integer multiple that fits the monitor,
falling back to smooth-scaled if no integer multiple fits.
"""

import pygame
import sys
from src.core.state_manager import StateManager
from src.core.input_handler import InputHandler
from src.states.menu import MenuState

# ── Palette ──────────────────────────────────────────────────────────────────
OBSIDIAN       = (10,  8, 14)
DARK_MAROON    = (42,  6, 12)
DEEP_CRIMSON   = (90, 10, 20)
CANDLE_GOLD    = (220, 160, 40)
GHOST_WHITE    = (230, 225, 235)

# ── Engine constants ──────────────────────────────────────────────────────────
NATIVE_W, NATIVE_H = 320, 180
TARGET_FPS         = 60
WINDOW_TITLE       = "Nocturne of Paws"


class Engine:
    def __init__(self):
        pygame.init()
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        pygame.display.set_caption(WINDOW_TITLE)

        # Pixel-perfect scaling: find best integer scale for the current display
        info = pygame.display.Info()
        self.scale = max(1, min(info.current_w // NATIVE_W,
                                info.current_h // NATIVE_H))

        win_w = NATIVE_W * self.scale
        win_h = NATIVE_H * self.scale

        self.screen = pygame.display.set_mode(
            (win_w, win_h),
            pygame.RESIZABLE,
        )
        # The canonical low-res canvas everything is drawn onto
        self.canvas = pygame.Surface((NATIVE_W, NATIVE_H))

        self.clock       = pygame.time.Clock()
        self.running     = False
        self.input       = InputHandler()
        self.state_mgr   = StateManager(self)

        # Cinematic zoom (post-process on the canvas). 1.0 = native.
        # render_focus is a canvas-space point (x, y) kept centred while zoomed.
        self.render_zoom  = 1.0
        self.render_focus = (NATIVE_W // 2, NATIVE_H // 2)

        # Boot into the main menu
        self.state_mgr.push(MenuState(self))

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _recalc_scale(self):
        """Re-evaluate scale factor when the window is resized."""
        w, h = self.screen.get_size()
        self.scale = max(1, min(w // NATIVE_W, h // NATIVE_H))

    # ── Main loop ─────────────────────────────────────────────────────────────

    def run(self):
        self.running = True
        while self.running:
            dt = self.clock.tick(TARGET_FPS) / 1000.0  # seconds

            # ── Events ────────────────────────────────────────────────────────
            raw_events = pygame.event.get()
            self.input.process(raw_events)

            for event in raw_events:
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.VIDEORESIZE:
                    self._recalc_scale()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False

            # ── Update ────────────────────────────────────────────────────────
            self.state_mgr.update(dt)

            # ── Draw to canvas ────────────────────────────────────────────────
            self.canvas.fill(DARK_MAROON)
            self.state_mgr.draw(self.canvas)

            # ── Cinematic zoom (crop a focused sub-rect of the canvas) ────────
            frame = self.canvas
            if self.render_zoom > 1.001:
                z      = self.render_zoom
                crop_w = max(1, int(NATIVE_W / z))
                crop_h = max(1, int(NATIVE_H / z))
                fx, fy = self.render_focus
                cx = max(0, min(int(fx - crop_w / 2), NATIVE_W - crop_w))
                cy = max(0, min(int(fy - crop_h / 2), NATIVE_H - crop_h))
                sub = self.canvas.subsurface(pygame.Rect(cx, cy, crop_w, crop_h))
                frame = pygame.transform.scale(sub, (NATIVE_W, NATIVE_H))

            # ── Post-zoom overlay: HUD/verse drawn crisp at native res ────────
            self.state_mgr.draw_overlay(frame)

            # ── Scale canvas → display ────────────────────────────────────────
            sw, sh = self.screen.get_size()
            scaled_w = NATIVE_W * self.scale
            scaled_h = NATIVE_H * self.scale
            scaled = pygame.transform.scale(frame, (scaled_w, scaled_h))

            # Centre the scaled canvas with letterbox/pillarbox in DARK_MAROON
            self.screen.fill(OBSIDIAN)
            blit_x = (sw - scaled_w) // 2
            blit_y = (sh - scaled_h) // 2
            self.screen.blit(scaled, (blit_x, blit_y))

            pygame.display.flip()

        pygame.quit()
        sys.exit()
