"""
Keyboard / gamepad input handler.

Provides a clean action-map abstraction so game code never touches raw keycodes.
Actions: move_left, move_right, move_up, move_down, jump, interact, run, pause.
"""

import pygame


# ── Default key bindings ──────────────────────────────────────────────────────
DEFAULT_BINDINGS = {
    "move_left":  [pygame.K_LEFT,  pygame.K_a],
    "move_right": [pygame.K_RIGHT, pygame.K_d],
    "move_up":    [pygame.K_UP,    pygame.K_w],
    "move_down":  [pygame.K_DOWN,  pygame.K_s],
    "jump":       [pygame.K_SPACE, pygame.K_z],
    "interact":   [pygame.K_RETURN, pygame.K_e, pygame.K_x],
    "run":        [pygame.K_LSHIFT, pygame.K_RSHIFT],
    "pause":      [pygame.K_ESCAPE, pygame.K_p],
    "rest":       [pygame.K_h, pygame.K_LCTRL],   # hold-to-cuddle / anchor shield
}


class InputHandler:
    def __init__(self, bindings=None):
        self._bindings   = bindings or DEFAULT_BINDINGS
        self._held       = set()   # actions currently held
        self._pressed    = set()   # actions pressed this frame
        self._released   = set()   # actions released this frame

        # Mouse
        self.mouse_pos    = (0, 0)
        self.mouse_left   = False
        self.mouse_right  = False
        self.mouse_left_pressed  = False
        self.mouse_right_pressed = False

    # ── Frame lifecycle ───────────────────────────────────────────────────────

    def process(self, events):
        """Call once per frame with the pygame event list."""
        self._pressed.clear()
        self._released.clear()
        self.mouse_left_pressed  = False
        self.mouse_right_pressed = False

        for event in events:
            if event.type == pygame.KEYDOWN:
                for action, keys in self._bindings.items():
                    if event.key in keys:
                        self._pressed.add(action)
                        self._held.add(action)

            elif event.type == pygame.KEYUP:
                for action, keys in self._bindings.items():
                    if event.key in keys:
                        self._released.add(action)
                        self._held.discard(action)

            elif event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.mouse_left = True
                    self.mouse_left_pressed = True
                elif event.button == 3:
                    self.mouse_right = True
                    self.mouse_right_pressed = True

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.mouse_left = False
                elif event.button == 3:
                    self.mouse_right = False

    # ── Query API ─────────────────────────────────────────────────────────────

    def held(self, action: str) -> bool:
        """True while the key is held down."""
        return action in self._held

    def pressed(self, action: str) -> bool:
        """True only on the frame the key was first pressed."""
        return action in self._pressed

    def released(self, action: str) -> bool:
        """True only on the frame the key was released."""
        return action in self._released

    def get_axis(self) -> tuple[float, float]:
        """Return (dx, dy) normalized directional input from -1 to 1."""
        dx = (1 if self.held("move_right") else 0) - (1 if self.held("move_left") else 0)
        dy = (1 if self.held("move_down")  else 0) - (1 if self.held("move_up")   else 0)
        return float(dx), float(dy)
