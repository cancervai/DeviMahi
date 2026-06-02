"""
CompanionMahi — ethereal white cat companion.

Follows Masum at a gentle lag; floats slightly off the ground (ethereal).
Emits a soft glow aura that pulses with the Oxytocin bond meter.
"""

import math
import pygame

MAHI_WHITE  = (230, 220, 235)
MAHI_EYE    = (180, 120, 200)   # violet-lavender eyes
MAHI_COLLAR = (200, 160,  40)   # gold collar
MAHI_GLOW   = (200, 180, 220)

FOLLOW_DIST  = 24    # target distance behind player (pixels)
FOLLOW_SPEED = 90.0


class CompanionMahi:
    def __init__(self, x: float, y: float):
        self.rect    = pygame.Rect(int(x), int(y), 8, 10)
        self._fx     = float(x)
        self._fy     = float(y)
        self._anim_t = 0.0
        self._frame  = 0
        self._sprite = self._build_sprite()

        # Lunar light level 0..1 — dims when the Storm bites her unshielded.
        self.light    = 1.0
        self.pressing = False   # hazard-press: hug Masum's side
        self.cuddling = False   # cuddle pose at a vista

    # ── Sprite ────────────────────────────────────────────────────────────────

    def _build_sprite(self) -> list[pygame.Surface]:
        frames = []
        for f in range(2):
            surf = pygame.Surface((8, 10), pygame.SRCALPHA)
            pixels = [
                "  WWWW  ",
                " WWWWWW ",
                "WWWWWWWW",
                "WWWWWWW ",
                " WWWWWW ",
                " WW  WW ",
                " W    W ",
            ]
            leg = [" W    W "] if f == 0 else ["W      W"]
            pixels += leg + [" W    W ", "  W  W  "]
            for row, line in enumerate(pixels[:10]):
                for col, ch in enumerate(line):
                    if ch == "W":
                        surf.set_at((col, row), MAHI_WHITE)
            surf.set_at((2, 2), MAHI_EYE)
            surf.set_at((5, 2), MAHI_EYE)
            for col in range(2, 6):
                surf.set_at((col, 5), MAHI_COLLAR)
            frames.append(surf)
        return frames

    # ── Update ────────────────────────────────────────────────────────────────

    def update(self, dt: float, target_rect: pygame.Rect):
        # Recover light gently when safe.
        self.light = min(1.0, self.light + dt * 0.15)

        # When pressing (hazard) or cuddling, close right up against Masum.
        follow_dist = 4 if (self.pressing or self.cuddling) else FOLLOW_DIST
        speed_mul   = 2.0 if self.pressing else 1.0

        # Target position: slightly behind and alongside the player
        tx = target_rect.x - follow_dist
        ty = target_rect.y

        # Lerp toward target
        dx = tx - self._fx
        dy = ty - self._fy
        dist = math.hypot(dx, dy)

        if dist > 4:
            speed = min(FOLLOW_SPEED * speed_mul * dt, dist)
            self._fx += (dx / dist) * speed
            self._fy += (dy / dist) * speed

        # Ethereal hover: gentle sine bob
        hover = math.sin(self._anim_t * 3.0) * 1.5
        self.rect.x = int(self._fx)
        self.rect.y = int(self._fy + hover)

        self._anim_t += dt
        if dist > 10:
            self._frame = int(self._anim_t * 5) % 2
        else:
            self._frame = 0

    # ── Draw ──────────────────────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface, camera):
        sx, sy = camera.world_to_screen(self.rect.x, self.rect.y)

        # Soft lunar glow aura — radius and brightness scale with self.light
        base_r = int(6 + 2 * math.sin(self._anim_t * 2.5))
        glow_r = max(2, int(base_r * (0.4 + 0.6 * self.light)))
        glow_surf = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        for r in range(glow_r, 0, -1):
            alpha = int(15 * self.light * (r / glow_r))
            pygame.draw.circle(glow_surf, (*MAHI_GLOW, alpha),
                                (glow_r, glow_r), r)
        surface.blit(glow_surf, (sx + 4 - glow_r, sy + 5 - glow_r))

        # Body dims as her light fades.
        sprite = self._sprite[self._frame]
        if self.light < 0.99:
            sprite = sprite.copy()
            tint = int(255 * (0.45 + 0.55 * self.light))
            sprite.fill((tint, tint, tint, 255), special_flags=pygame.BLEND_RGBA_MULT)
        surface.blit(sprite, (sx, sy))
