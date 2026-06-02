"""
Dialogue system — gothic text-box with typewriter effect and speaker portrait.

Usage:
    dialogue.queue([("Masum", "...The Citadel smells of old roses."),
                    ("Mahi",  "Stay close.")])
"""

import pygame

BOX_H       = 40
BOX_MARGIN  = 4
TEXT_SPEED  = 28    # characters per second

DARK_MAROON = (32,  4,  8)
BORDER_COL  = (120, 30, 40)
SPEAKER_COL = (220, 160, 40)
TEXT_COL    = (220, 210, 220)
BG_ALPHA    = 210


class DialogueSystem:
    def __init__(self):
        self._queue: list[tuple[str, str]] = []
        self._active      = False
        self._speaker     = ""
        self._full_text   = ""
        self._visible_len = 0.0
        self._done        = False

    # ── API ───────────────────────────────────────────────────────────────────

    def queue(self, lines: list[tuple[str, str]]):
        self._queue.extend(lines)
        if not self._active:
            self._advance()

    def _advance(self):
        if not self._queue:
            self._active = False
            return
        self._speaker, self._full_text = self._queue.pop(0)
        self._visible_len = 0.0
        self._done        = False
        self._active      = True

    # ── Update ────────────────────────────────────────────────────────────────

    def update(self, dt: float, inp):
        if not self._active:
            return

        if not self._done:
            self._visible_len = min(len(self._full_text),
                                    self._visible_len + TEXT_SPEED * dt)
            if self._visible_len >= len(self._full_text):
                self._done = True
        else:
            if inp.pressed("interact"):
                self._advance()

        # Skip typewriter on interact
        if not self._done and inp.pressed("interact"):
            self._visible_len = float(len(self._full_text))

    # ── Draw ──────────────────────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface):
        if not self._active:
            return

        w, h = surface.get_size()
        box_y = h - BOX_H - BOX_MARGIN

        # Semi-transparent box
        box = pygame.Surface((w - BOX_MARGIN * 2, BOX_H), pygame.SRCALPHA)
        box.fill((*DARK_MAROON, BG_ALPHA))
        surface.blit(box, (BOX_MARGIN, box_y))
        pygame.draw.rect(surface, BORDER_COL,
                         (BOX_MARGIN, box_y, w - BOX_MARGIN * 2, BOX_H), 1)

        font_name = pygame.font.SysFont("courier", 7, bold=True)
        font_text = pygame.font.SysFont("courier", 6)

        # Speaker name
        name_surf = font_name.render(self._speaker + ":", True, SPEAKER_COL)
        surface.blit(name_surf, (BOX_MARGIN + 4, box_y + 4))

        # Typewriter text — word-wrap at ~50 chars
        visible = self._full_text[:int(self._visible_len)]
        lines   = self._wrap(visible, max_chars=48)
        for i, line in enumerate(lines[:3]):
            txt = font_text.render(line, True, TEXT_COL)
            surface.blit(txt, (BOX_MARGIN + 4, box_y + 14 + i * 9))

        # Continue indicator
        if self._done:
            blink = pygame.time.get_ticks() % 800 < 400
            if blink:
                ind = font_text.render("▼", True, SPEAKER_COL)
                surface.blit(ind, (w - BOX_MARGIN - 10, box_y + BOX_H - 10))

    @staticmethod
    def _wrap(text: str, max_chars: int) -> list[str]:
        words  = text.split(" ")
        lines  = []
        current = ""
        for word in words:
            if len(current) + len(word) + 1 <= max_chars:
                current += ("" if not current else " ") + word
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines
