"""
Weather & atmosphere system — the world is always moving.

Layers (back→front):
    • fog       : slow rolling ground mist bands
    • fireflies : drifting amber motes that pulse
    • petals    : red rose petals tumbling on the wind
    • stars     : falling stars (Act III / cosmic moments)
    • storm     : "Storm of Shadows" — biting wind streaks + darkening veil

Each layer is independently toggleable so a scene can compose its own mood.
All particles live in *screen* space (already camera-resolved) so weather
reads as an atmospheric overlay rather than world geometry.
"""

import math
import random
import pygame

# Palette
ROSE_RED    = (150, 24, 38)
ROSE_DARK   = (96, 14, 26)
FIREFLY_AMB = (235, 180, 70)
FOG_GREY    = (60, 50, 64)
STAR_SILVER = (220, 215, 235)
SHADOW_COL  = (8, 4, 12)


class _Petal:
    __slots__ = ("x", "y", "vx", "vy", "spin", "ang", "size", "col")

    def __init__(self, w, h):
        self.x    = random.uniform(0, w)
        self.y    = random.uniform(-h, 0)
        self.vx   = random.uniform(-14, -4)
        self.vy   = random.uniform(10, 22)
        self.spin = random.uniform(-3, 3)
        self.ang  = random.uniform(0, math.tau)
        self.size = random.choice((1, 2, 2))
        self.col  = random.choice((ROSE_RED, ROSE_DARK))

    def update(self, dt, wind):
        self.ang += self.spin * dt
        self.x   += (self.vx + wind + math.sin(self.ang) * 8) * dt
        self.y   += self.vy * dt

    def offscreen(self, w, h):
        return self.y > h + 4 or self.x < -6


class _Firefly:
    __slots__ = ("x", "y", "phase", "speed", "drift")

    def __init__(self, w, h):
        self.x     = random.uniform(0, w)
        self.y     = random.uniform(0, h)
        self.phase = random.uniform(0, math.tau)
        self.speed = random.uniform(0.6, 1.8)
        self.drift = random.uniform(4, 12)

    def update(self, dt, t):
        self.x += math.sin(t * self.speed + self.phase) * self.drift * dt
        self.y += math.cos(t * self.speed * 0.7 + self.phase) * self.drift * 0.5 * dt


class _Star:
    __slots__ = ("x", "y", "vx", "vy", "life")

    def __init__(self, w, h):
        self.x    = random.uniform(0, w)
        self.y    = random.uniform(-20, 0)
        self.vx   = random.uniform(-40, -80)
        self.vy   = random.uniform(60, 120)
        self.life = 1.0


class Weather:
    def __init__(self, w: int, h: int):
        self.w, self.h = w, h
        self.t = 0.0

        # Toggles
        self.fog       = True
        self.fireflies = True
        self.petals    = True
        self.stars     = False
        self.storm     = 0.0    # 0..1 intensity (drives Anchor mechanic visuals)

        self.wind      = 0.0    # extra horizontal push (storm cranks this)

        self._petals    = [_Petal(w, h) for _ in range(26)]
        self._fireflies = [_Firefly(w, h) for _ in range(14)]
        self._stars     = []
        self._fog_off   = 0.0

    # ── Update ────────────────────────────────────────────────────────────────

    def update(self, dt: float):
        self.t       += dt
        self._fog_off += dt * 6
        gust = self.wind - self.storm * 60

        if self.petals:
            for p in self._petals:
                p.update(dt, gust)
                if p.offscreen(self.w, self.h):
                    p.__init__(self.w, self.h)

        if self.fireflies:
            for f in self._fireflies:
                f.update(dt, self.t)
                f.x %= self.w
                f.y %= self.h

        if self.stars or self.storm > 0:
            spawn_rate = (3 if self.stars else 0) + int(self.storm * 8)
            for _ in range(spawn_rate):
                if random.random() < 0.4:
                    self._stars.append(_Star(self.w, self.h))
        for s in self._stars:
            s.x += s.vx * dt
            s.y += s.vy * dt
            s.life -= dt * 0.8
        self._stars = [s for s in self._stars if s.life > 0 and s.y < self.h + 10]

    # ── Draw ──────────────────────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface):
        if self.fog:
            self._draw_fog(surface)
        if self.fireflies:
            self._draw_fireflies(surface)
        if self.petals:
            self._draw_petals(surface)
        self._draw_stars(surface)
        if self.storm > 0:
            self._draw_storm(surface)

    def _draw_fog(self, surface):
        fog = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        bands = 3
        for b in range(bands):
            base_y = self.h - 14 - b * 10
            alpha  = 26 - b * 6
            off    = (self._fog_off * (0.4 + b * 0.3)) % self.w
            for layer_x in (-off, self.w - off):
                for i in range(0, self.w + 40, 24):
                    bob = math.sin((i + self._fog_off) * 0.05 + b) * 3
                    pygame.draw.ellipse(
                        fog, (*FOG_GREY, alpha),
                        (int(layer_x + i), int(base_y + bob), 40, 16))
        surface.blit(fog, (0, 0))

    def _draw_fireflies(self, surface):
        for f in self._fireflies:
            glow = 0.5 + 0.5 * math.sin(self.t * 2.5 + f.phase)
            a    = int(120 + 120 * glow)
            r, g, b = FIREFLY_AMB
            col = (r, int(g * (0.6 + 0.4 * glow)), int(b * glow))
            px, py = int(f.x), int(f.y)
            if glow > 0.7:
                halo = pygame.Surface((6, 6), pygame.SRCALPHA)
                pygame.draw.circle(halo, (*col, 40), (3, 3), 3)
                surface.blit(halo, (px - 3, py - 3))
            if 0 <= px < self.w and 0 <= py < self.h:
                surface.set_at((px, py), col)

    def _draw_petals(self, surface):
        for p in self._petals:
            px, py = int(p.x), int(p.y)
            if p.size == 1:
                if 0 <= px < self.w and 0 <= py < self.h:
                    surface.set_at((px, py), p.col)
            else:
                pygame.draw.rect(surface, p.col, (px, py, 2, 2))

    def _draw_stars(self, surface):
        for s in self._stars:
            a = max(0, min(255, int(s.life * 255)))
            x0, y0 = int(s.x), int(s.y)
            x1, y1 = int(s.x - s.vx * 0.04), int(s.y - s.vy * 0.04)
            pygame.draw.line(surface, STAR_SILVER, (x0, y0), (x1, y1))
            if 0 <= x0 < self.w and 0 <= y0 < self.h:
                surface.set_at((x0, y0), (255, 255, 255))

    def _draw_storm(self, surface):
        s = self.storm
        # Darkening veil
        veil = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        veil.fill((*SHADOW_COL, int(150 * s)))
        surface.blit(veil, (0, 0))
        # Biting wind streaks
        n = int(20 * s)
        for _ in range(n):
            y  = random.uniform(0, self.h)
            x  = random.uniform(0, self.w)
            ln = random.uniform(20, 60) * s
            shade = int(40 + 60 * random.random())
            pygame.draw.line(surface, (shade, shade // 2, shade),
                             (int(x), int(y)), (int(x - ln), int(y + ln * 0.2)))
