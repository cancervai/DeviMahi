"""
Core game engine: pixel-perfect window, game loop, delta-time, scaling.

Internal canvas: 320x180 (native 8-bit resolution).
Displayed surface: largest integer multiple that fits the monitor,
falling back to smooth-scaled if no integer multiple fits.
"""

import asyncio
import sys
import pygame
from src.core.state_manager import StateManager
from src.core.input_handler import InputHandler
from src.states.menu import MenuState

# True when running in the browser (pygbag / Emscripten).
IS_WEB = sys.platform in ("emscripten", "wasi")

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
        # Audio may be unavailable until a user gesture in the browser; never fatal.
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        except pygame.error:
            pass
        pygame.display.set_caption(WINDOW_TITLE)

        # Pixel-perfect scaling: pick the best integer scale that fits the display.
        try:
            info = pygame.display.Info()
            avail_w, avail_h = info.current_w, info.current_h
        except pygame.error:
            avail_w, avail_h = NATIVE_W * 4, NATIVE_H * 4
        if not avail_w or avail_w <= 0:
            avail_w, avail_h = NATIVE_W * 4, NATIVE_H * 4
        self.scale = max(1, min(avail_w // NATIVE_W, avail_h // NATIVE_H))

        win_w = NATIVE_W * self.scale
        win_h = NATIVE_H * self.scale

        # The browser owns the canvas size; a fixed window scales cleanly there.
        flags = 0 if IS_WEB else pygame.RESIZABLE
        self.screen = pygame.display.set_mode((win_w, win_h), flags)
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

    def _tick(self, dt: float):
        """Advance and render exactly one frame."""
        # ── Events ────────────────────────────────────────────────────────────
        raw_events = pygame.event.get()
        self.input.process(raw_events)

        for event in raw_events:
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                self._recalc_scale()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                # On the web, Esc shouldn't kill the tab; let states handle "pause".
                if not IS_WEB:
                    self.running = False

        # ── Update ──────────────────────────────────────────────────────────────
        self.state_mgr.update(dt)

        # ── Draw to canvas ────────────────────────────────────────────────────────
        self.canvas.fill(DARK_MAROON)
        self.state_mgr.draw(self.canvas)

        # ── Cinematic zoom (crop a focused sub-rect of the canvas) ────────────────
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

        # ── Post-zoom overlay: HUD/verse drawn crisp at native res ────────────────
        self.state_mgr.draw_overlay(frame)

        # ── Scale canvas → display ────────────────────────────────────────────────
        sw, sh = self.screen.get_size()
        scaled_w = NATIVE_W * self.scale
        scaled_h = NATIVE_H * self.scale
        scaled = pygame.transform.scale(frame, (scaled_w, scaled_h))

        self.screen.fill(OBSIDIAN)
        self.screen.blit(scaled, ((sw - scaled_w) // 2, (sh - scaled_h) // 2))
        pygame.display.flip()

    async def run_async(self):
        """Async game loop — required by pygbag/WASM, also fine natively."""
        self.running = True
        while self.running:
            dt = self.clock.tick(TARGET_FPS) / 1000.0
            self._tick(dt)
            await asyncio.sleep(0)   # yield to the browser event loop
        pygame.quit()

    def run(self):
        """Blocking entry point for native desktop."""
        asyncio.run(self.run_async())
        if not IS_WEB:
            sys.exit()
