"""
PlayerMasum — midnight-black cat protagonist.

Movement: walk / run left-right, jump with coyote-time and jump-buffering.
The sprite is procedurally drawn (8x8 pixel art cat silhouette) until
real sprites are loaded from /assets/sprites/.
"""

import pygame

GRAVITY       = 480.0
JUMP_SPEED    = -200.0
WALK_SPEED    = 70.0
RUN_SPEED     = 130.0
COYOTE_TIME   = 0.10   # seconds of grace after walking off a ledge
JUMP_BUFFER   = 0.12   # seconds a jump input is buffered before landing

# Masum's pixel-art body color
MASUM_BLACK   = (18, 12, 22)
MASUM_EYE     = (60, 200, 120)    # eerie green eyes
MASUM_COLLAR  = (140, 20, 30)     # deep crimson collar


class PlayerMasum:
    def __init__(self, x: float, y: float):
        self.rect   = pygame.Rect(int(x), int(y), 8, 10)
        self._vx    = 0.0
        self._vy    = 0.0
        self._on_ground = False
        self._facing    = 1         # 1=right, -1=left
        self._coyote    = 0.0
        self._jump_buf  = 0.0
        self._anim_t    = 0.0
        self._frame     = 0
        self._sprite    = self._build_sprite()

    # ── Sprite (procedural pixel art) ─────────────────────────────────────────

    def _build_sprite(self) -> list[pygame.Surface]:
        """Two-frame walk cycle pixel art: 8×10 silhouette."""
        frames = []
        for f in range(2):
            surf = pygame.Surface((8, 10), pygame.SRCALPHA)
            # Body
            pixels = [
                "  BBBB  ",
                " BBBBBB ",
                "BBBBBBBB",
                "BBBBBBB ",
                " BBBBBB ",
                " BB  BB ",
                " B    B ",
            ]
            leg_a = [" B    B "] if f == 0 else ["B      B"]
            pixels += leg_a + [" B    B ", "  B  B  "]
            for row, line in enumerate(pixels[:10]):
                for col, ch in enumerate(line):
                    if ch == "B":
                        surf.set_at((col, row), MASUM_BLACK)
            # Eyes
            surf.set_at((2, 2), MASUM_EYE)
            surf.set_at((5, 2), MASUM_EYE)
            # Collar
            for col in range(2, 6):
                surf.set_at((col, 5), MASUM_COLLAR)
            frames.append(surf)
        return frames

    # ── Update ────────────────────────────────────────────────────────────────

    def update(self, dt: float, inp, floors: list[pygame.Rect]):
        self._jump_buf  = max(0.0, self._jump_buf  - dt)
        self._coyote    = max(0.0, self._coyote    - dt)

        # Horizontal movement
        dx, _ = inp.get_axis()
        speed = RUN_SPEED if inp.held("run") else WALK_SPEED
        self._vx = dx * speed
        if dx != 0:
            self._facing = int(dx)

        # Jump input buffering
        if inp.pressed("jump"):
            self._jump_buf = JUMP_BUFFER

        if self._jump_buf > 0 and (self._on_ground or self._coyote > 0):
            self._vy      = JUMP_SPEED
            self._jump_buf = 0
            self._coyote   = 0

        # Gravity
        self._vy += GRAVITY * dt
        if self._vy > 600:
            self._vy = 600

        # Move & collide
        self._on_ground = False
        self._move(dt, floors)

        # Coyote time: set when leaving ground
        if not self._on_ground and self._vy > 0:
            if self._coyote <= 0:
                self._coyote = 0  # already expired

        # Animation
        if abs(self._vx) > 1:
            self._anim_t += dt * (8 if inp.held("run") else 5)
            self._frame = int(self._anim_t) % 2
        else:
            self._frame = 0

    def _move(self, dt: float, floors: list[pygame.Rect]):
        # Horizontal
        self.rect.x += int(self._vx * dt)
        for floor in floors:
            if self.rect.colliderect(floor):
                if self._vx > 0:
                    self.rect.right = floor.left
                elif self._vx < 0:
                    self.rect.left  = floor.right
                self._vx = 0

        # Vertical
        prev_bottom = self.rect.bottom
        self.rect.y += int(self._vy * dt)
        for floor in floors:
            if self.rect.colliderect(floor):
                if self._vy > 0:
                    self.rect.bottom  = floor.top
                    self._vy          = 0
                    self._on_ground   = True
                    self._coyote      = COYOTE_TIME
                elif self._vy < 0:
                    self.rect.top     = floor.bottom
                    self._vy          = 0

    # ── Draw ──────────────────────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface, camera):
        sx, sy = camera.world_to_screen(self.rect.x, self.rect.y)
        sprite = self._sprite[self._frame]
        if self._facing == -1:
            sprite = pygame.transform.flip(sprite, True, False)
        surface.blit(sprite, (sx, sy))
