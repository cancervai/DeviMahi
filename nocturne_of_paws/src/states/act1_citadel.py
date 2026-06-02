"""
Act 1 — The Obsidian Citadel.

Side-scrolling exploration that binds together every signature mechanic:
  • Living weather  — rolling fog, drifting rose petals, fireflies
  • Hold-to-Cuddle  — at a gothic balcony vista, hold [REST] to embrace:
                      UI fades, camera zooms in, the Oxytocin meter fills,
                      and poetic verse gently blooms onto the screen.
  • The Anchor      — a "Storm of Shadows" sweeps in; hold [REST] to make
                      Masum dig in and shield Mahi. Fail and her light dims.
  • Waltz Checkpoint— a candle-lit stone circle launches the Touch-Waltz.
"""

import math
import pygame
from src.states.base_state import BaseState
from src.core.camera import Camera
from src.core.weather import Weather
from src.entities.player_masum import PlayerMasum
from src.entities.companion_mahi import CompanionMahi
from src.entities.npc_frogs import NpcFrog
from src.ui.dialogue_system import DialogueSystem
from src.ui.oxytocin_meter import OxytocinMeter

NATIVE_W, NATIVE_H = 320, 180
WORLD_W,  WORLD_H  = 1280, 360

OBSIDIAN     = (10,   8,  14)
DARK_MAROON  = (42,   6,  12)
DEEP_CRIMSON = (90,  10,  20)
STONE_GREY   = (55,  48,  60)
CANDLE_GOLD  = (220, 160,  40)
GHOST_WHITE  = (230, 225, 235)

# ── Poetic verse revealed while cuddling ──────────────────────────────────────
CUDDLE_VERSE = [
    "The Cold devours the stars, one frozen breath at a time...",
    "But here, in the curl of your tail, I have forgotten winter.",
    "Stay. Let the kingdom crumble.",
    "We are the last warm thing the dark has left to fear.",
]

# Storm cadence
STORM_INTERVAL = 14.0   # seconds of calm before a storm sweeps in
STORM_LENGTH   = 6.0    # how long a storm bites
LIGHT_DRAIN    = 0.35   # Mahi's light lost per second when unshielded


class Act1CitadelState(BaseState):
    def __init__(self, engine):
        super().__init__(engine)
        self.camera    = Camera(NATIVE_W, NATIVE_H, WORLD_W, WORLD_H)
        self.weather   = Weather(NATIVE_W, NATIVE_H)
        self.player    = PlayerMasum(64, WORLD_H - 64)
        self.companion = CompanionMahi(96, WORLD_H - 64)
        self.frogs     = [NpcFrog(360 + i * 150, WORLD_H - 40) for i in range(4)]
        self.dialogue  = DialogueSystem()
        self.oxytocin  = OxytocinMeter(initial=18)
        self._floors   = self._build_floors()
        self._timer    = 0.0

        # ── Mechanic zones (world space) ─────────────────────────────────────
        self.vista_zone   = pygame.Rect(980, WORLD_H - 120, 120, 120)
        self.checkpoint   = pygame.Rect(560, WORLD_H - 48, 80, 48)
        self._cp_fired    = False

        # ── Cuddle state ──────────────────────────────────────────────────────
        self._cuddle_blend = 0.0     # 0 = normal, 1 = full embrace
        self._cuddle_hold  = 0.0     # seconds held (drives verse reveal)
        self._verse_idx    = -1

        # ── Storm state ───────────────────────────────────────────────────────
        self._storm_clock  = STORM_INTERVAL
        self._storm_active = 0.0     # remaining seconds, 0 = calm
        self._storm_warned = False

    # ── World geometry ────────────────────────────────────────────────────────

    def _build_floors(self):
        return [
            pygame.Rect(0,    WORLD_H - 16, WORLD_W, 16),   # ground
            pygame.Rect(200,  WORLD_H - 56,  96, 8),
            pygame.Rect(400,  WORLD_H - 80,  64, 8),
            pygame.Rect(720,  WORLD_H - 56, 112, 8),
            pygame.Rect(880,  WORLD_H - 96,  80, 8),
            pygame.Rect(1120, WORLD_H - 80,  96, 8),
        ]

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def on_enter(self):
        self.dialogue.queue([
            ("Masum", "...The Citadel smells of old roses and iron."),
            ("Mahi",  "Stay close. The corridors remember those who wander."),
        ])

    def on_resume(self):
        # Returning from the Waltz — reset any cinematic zoom.
        self.engine.render_zoom = 1.0

    # ── Update ────────────────────────────────────────────────────────────────

    def update(self, dt):
        self._timer += dt

        resting = self.input.held("rest") or self.input.mouse_left

        self._update_storm(dt, resting)
        self._update_cuddle(dt, resting)

        # Movement is suspended while embracing.
        self.player.update(dt, self.input, self._floors)
        self.companion.update(dt, self.player.rect)
        for frog in self.frogs:
            frog.update(dt)
        self.dialogue.update(dt, self.input)
        self.oxytocin.update(dt)
        self.weather.update(dt)
        self._update_camera_and_zoom(dt)
        self._update_checkpoint()

        if self.input.pressed("pause"):
            from src.states.menu import MenuState
            self.state_mgr.push(MenuState(self.engine))

    # ── Hold-to-Cuddle ────────────────────────────────────────────────────────

    def _in_vista(self) -> bool:
        return self.vista_zone.colliderect(self.player.rect)

    def _update_cuddle(self, dt, resting):
        active = self._in_vista() and resting and self._storm_active <= 0

        if active:
            self._cuddle_blend = min(1.0, self._cuddle_blend + dt * 1.6)
            self._cuddle_hold += dt
            # Fill the bond and reveal verse line-by-line as the embrace deepens.
            self.oxytocin.increase(dt * 6.0)
            idx = min(len(CUDDLE_VERSE) - 1, int(self._cuddle_hold / 2.2))
            self._verse_idx = idx
        else:
            self._cuddle_blend = max(0.0, self._cuddle_blend - dt * 2.2)
            if self._cuddle_blend <= 0:
                self._cuddle_hold = 0.0
                self._verse_idx   = -1

        cuddling = self._cuddle_blend > 0.05
        self.player.cuddling    = cuddling
        self.companion.cuddling = cuddling

    # ── The Anchor / Storm of Shadows ─────────────────────────────────────────

    def _update_storm(self, dt, resting):
        if self._storm_active > 0:
            self._storm_active -= dt
            self.weather.storm = min(1.0, self.weather.storm + dt * 2)
            self.companion.pressing = True

            # Anchor: holding REST shields Mahi. Otherwise her light drains.
            shielded = resting
            self.player.frozen = shielded     # digs claws in, can't move
            if not shielded:
                self.companion.light = max(0.05, self.companion.light - LIGHT_DRAIN * dt)

            if self._storm_active <= 0:
                self._storm_active = 0.0
                self._storm_warned = False
                self.player.frozen = False
                self.companion.pressing = False
                self.dialogue.queue([("Mahi", "...It passes. You held the dark at bay.")])
        else:
            self.weather.storm = max(0.0, self.weather.storm - dt * 1.5)
            self._storm_clock -= dt
            if self._storm_clock <= 1.2 and not self._storm_warned:
                self._storm_warned = True
                self.dialogue.queue([("Mahi", "Something cold is coming. Hold me!")])
            if self._storm_clock <= 0:
                self._storm_clock  = STORM_INTERVAL
                self._storm_active = STORM_LENGTH

    # ── Camera + cinematic zoom ───────────────────────────────────────────────

    def _update_camera_and_zoom(self, dt):
        self.camera.update(self.player.rect, dt)

        # Zoom in on the embrace; otherwise rest at native scale.
        target_zoom = 1.0 + 0.7 * self._cuddle_blend
        self.engine.render_zoom += (target_zoom - self.engine.render_zoom) * min(1.0, dt * 4)

        # Focus midway between the two cats, in canvas space.
        px, py = self.camera.world_to_screen(self.player.rect.centerx, self.player.rect.centery)
        mx, my = self.camera.world_to_screen(self.companion.rect.centerx, self.companion.rect.centery)
        self.engine.render_focus = ((px + mx) // 2, (py + my) // 2 - 4)

    # ── Waltz checkpoint ──────────────────────────────────────────────────────

    def _update_checkpoint(self):
        if not self._cp_fired and self.checkpoint.colliderect(self.player.rect):
            self._cp_fired = True
            from src.states.waltz_minigame import WaltzMinigameState
            self.state_mgr.push(WaltzMinigameState(self.engine))

    # ── Draw ──────────────────────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface):
        surface.fill(OBSIDIAN)
        self._draw_background(surface)
        self._draw_floors(surface)
        self._draw_checkpoint(surface)
        self._draw_vista(surface)
        for frog in self.frogs:
            frog.draw(surface, self.camera)
        self.companion.draw(surface, self.camera)
        self.player.draw(surface, self.camera)

        # Weather overlays the world (it zooms with the embrace).
        self.weather.draw(surface)

    def draw_overlay(self, surface):
        """Crisp, full-frame HUD pass — runs after the cinematic zoom crop."""
        # HUD and dialogue fade away during the embrace so verse stands alone.
        if self._cuddle_blend < 0.5:
            self.oxytocin.draw(surface)
            self.dialogue.draw(surface)
        self._draw_prompts(surface)
        self._draw_cuddle_overlay(surface)

    def _draw_background(self, surface):
        w, h = surface.get_size()
        ox, _ = self.camera.offset

        for i in range(6):
            wx = i * 220 - (ox * 0.2 % 220)
            pygame.draw.rect(surface, (25, 12, 20), (int(wx), 10, 40, 60))
            pygame.draw.arc(surface, (35, 16, 28),
                            pygame.Rect(int(wx), 10, 40, 30), 0, math.pi, 2)

        for i in range(8):
            sx = int(i * 160 - (ox * 0.5 % 160))
            tower_h = 40 + (i % 3) * 15
            pygame.draw.rect(surface, STONE_GREY, (sx, h - tower_h - 16, 10, tower_h))
            pygame.draw.polygon(surface, (45, 38, 50),
                                [(sx, h - tower_h - 16),
                                 (sx + 5, h - tower_h - 28),
                                 (sx + 10, h - tower_h - 16)])

        for i in range(4):
            cx = int(i * 300 + 80 - (ox * 0.3 % 300))
            cy = 30 + (i % 2) * 20
            flicker = math.sin(self._timer * 5 + i * 1.3) * 2
            pygame.draw.circle(surface, CANDLE_GOLD, (cx % w, cy), max(1, int(3 + flicker)))

    def _draw_floors(self, surface):
        for rect in self._floors:
            sr = self.camera.apply(rect)
            pygame.draw.rect(surface, STONE_GREY, sr)
            pygame.draw.line(surface, (80, 65, 75), sr.topleft, sr.topright)

    def _draw_checkpoint(self, surface):
        """Candle-lit stone circle — the Waltz save point."""
        cx, cy = self.camera.world_to_screen(self.checkpoint.centerx, self.checkpoint.bottom - 2)
        if -40 < cx < NATIVE_W + 40:
            pygame.draw.ellipse(surface, (40, 36, 46), (cx - 26, cy - 6, 52, 12))
            pygame.draw.ellipse(surface, (70, 62, 74), (cx - 26, cy - 6, 52, 12), 1)
            for k in range(-2, 3):
                kx = cx + k * 11
                flick = math.sin(self._timer * 6 + k) * 1.5
                pygame.draw.rect(surface, (150, 100, 30), (kx - 1, cy - 10, 2, 5))
                pygame.draw.circle(surface, CANDLE_GOLD, (kx, cy - 12 + int(flick * 0.5)),
                                   max(1, int(2 + flick)))

    def _draw_vista(self, surface):
        """Gothic balcony railing overlooking the misty swamp."""
        bx, by = self.camera.world_to_screen(self.vista_zone.x, self.vista_zone.bottom)
        if bx > NATIVE_W or bx + self.vista_zone.w < 0:
            return
        rail_y = by - 14
        pygame.draw.rect(surface, STONE_GREY, (bx, rail_y, self.vista_zone.w, 3))
        for k in range(0, self.vista_zone.w, 8):
            pygame.draw.rect(surface, (70, 62, 74), (bx + k, rail_y, 2, 12))

    def _draw_prompts(self, surface):
        w, h = surface.get_size()
        font = pygame.font.SysFont("courier", 6)

        if self._storm_active > 0:
            txt = "[ HOLD to ANCHOR — shield Mahi! ]"
            col = (230, 90, 90) if (self._timer * 4) % 1 < 0.6 else (150, 50, 50)
            s = font.render(txt, True, col)
            surface.blit(s, (w // 2 - s.get_width() // 2, 24))
        elif self._in_vista() and self._cuddle_blend < 0.05:
            txt = "[ Hold to Rest ]"
            a = int(150 + 100 * math.sin(self._timer * 2))
            s = font.render(txt, True, (a // 2, a // 3, a // 2 + 40))
            surface.blit(s, (w // 2 - s.get_width() // 2, h - 30))

    def _draw_cuddle_overlay(self, surface):
        if self._cuddle_blend <= 0.02:
            return
        w, h = surface.get_size()

        # Tender vignette deepening with the embrace. After the zoom crop the
        # focus point sits at frame centre, so the warm hole punches there.
        vig = pygame.Surface((w, h), pygame.SRCALPHA)
        vig.fill((6, 2, 8, int(150 * self._cuddle_blend)))
        pygame.draw.circle(vig, (0, 0, 0, 0), (w // 2, h // 2 - 6), 44)
        surface.blit(vig, (0, 0))

        # Poetic verse, gently faded in.
        if self._verse_idx >= 0:
            font = pygame.font.SysFont("times new roman", 8, italic=True)
            line_a = min(1.0, (self._cuddle_hold % 2.2) / 0.8)
            for i in range(self._verse_idx + 1):
                alpha = 255 if i < self._verse_idx else int(255 * line_a)
                col = (235, 215, 225)
                s = font.render(CUDDLE_VERSE[i], True, col)
                s.set_alpha(int(alpha * min(1.0, self._cuddle_blend * 1.4)))
                surface.blit(s, (w // 2 - s.get_width() // 2, h - 52 + i * 11))
