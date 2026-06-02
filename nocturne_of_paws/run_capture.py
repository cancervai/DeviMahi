"""
Headless execution harness — drives the engine through every state and
mechanic with simulated input, saving real rendered frames as proof.

Frames cover: menu, citadel + weather, the Waltz checkpoint, the
Hold-to-Cuddle embrace (zoom + verse), and the Storm-of-Shadows Anchor.
"""
import sys, os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import pygame
pygame.init()
pygame.display.set_mode((320, 180))

from core.engine import Engine
from states.act1_citadel import Act1CitadelState, STORM_LENGTH
from states.waltz_minigame import WaltzMinigameState


class FakeInput:
    def __init__(self):
        self._held = set(); self._pressed = set()
        self.mouse_pos = (0, 0)
        self.mouse_left = self.mouse_right = False
        self.mouse_left_pressed = self.mouse_right_pressed = False
    def hold(self, *a): self._held = set(a)
    def press(self, *a): self._pressed = set(a)
    def clear(self): self._pressed = set()
    def held(self, a): return a in self._held
    def pressed(self, a): return a in self._pressed
    def released(self, a): return False
    def get_axis(self):
        dx = (1 if self.held("move_right") else 0) - (1 if self.held("move_left") else 0)
        dy = (1 if self.held("move_down") else 0) - (1 if self.held("move_up") else 0)
        return float(dx), float(dy)


def step(engine, fake, dt=1/60):
    """One full engine frame including the post-zoom overlay pass."""
    from core.engine import NATIVE_W, NATIVE_H, OBSIDIAN
    engine.canvas.fill((42, 6, 12))
    engine.state_mgr.update(dt)
    engine.state_mgr.draw(engine.canvas)
    # Reproduce engine's zoom+overlay compositing into `frame`
    frame = engine.canvas
    if engine.render_zoom > 1.001:
        z = engine.render_zoom
        cw = max(1, int(NATIVE_W / z)); ch = max(1, int(NATIVE_H / z))
        fx, fy = engine.render_focus
        cx = max(0, min(int(fx - cw / 2), NATIVE_W - cw))
        cy = max(0, min(int(fy - ch / 2), NATIVE_H - ch))
        sub = engine.canvas.subsurface(pygame.Rect(cx, cy, cw, ch))
        frame = pygame.transform.scale(sub, (NATIVE_W, NATIVE_H))
    engine.state_mgr.draw_overlay(frame)
    fake.clear()
    return frame


def save(frame, path, scale=4):
    pygame.image.save(pygame.transform.scale(frame, (320 * scale, 180 * scale)), path)
    print(f"  saved {os.path.basename(path)}")


def main():
    out = os.path.join(os.path.dirname(__file__), "screenshots")
    os.makedirs(out, exist_ok=True)

    engine = Engine()
    fake = FakeInput(); engine.input = fake
    print(f"Engine up. scale={engine.scale}")

    # 1) MAIN MENU
    for _ in range(30): f = step(engine, fake)
    save(f, os.path.join(out, "01_main_menu.png"))

    # 2) ACT 1 CITADEL — weather + opening dialogue
    act1 = Act1CitadelState(engine)
    engine.state_mgr.replace(act1)
    for _ in range(20): f = step(engine, fake)
    fake.press("interact"); f = step(engine, fake)
    for _ in range(40): f = step(engine, fake)   # let petals/fog/fireflies build
    save(f, os.path.join(out, "02_act1_citadel.png"))

    # 3) WALK RIGHT → hits Waltz checkpoint (~x=600)
    fake.hold("move_right", "run")
    f = None
    for _ in range(600):
        f = step(engine, fake)
        if isinstance(engine.state_mgr.current, WaltzMinigameState):
            break
    # Render a little waltz, simulate on-beat taps, capture, then return
    fake.hold()
    for _ in range(50): f = step(engine, fake)
    for _ in range(6):
        fake.press("move_left", "move_right", "move_up", "move_down")
        f = step(engine, fake)
        for _ in range(10): f = step(engine, fake)
    save(f, os.path.join(out, "04_waltz_minigame.png"))
    engine.state_mgr.pop()                         # back to citadel
    f = step(engine, fake)
    print(f"  back to {type(engine.state_mgr.current).__name__}")

    # 4) WALK to the balcony VISTA (~x=980+) then HOLD-TO-CUDDLE
    fake.hold("move_right", "run")
    for _ in range(800):
        f = step(engine, fake)
        if act1.player.rect.centerx >= act1.vista_zone.centerx:
            break
    fake.hold("rest")                              # hold to embrace
    for _ in range(220): f = step(engine, fake)    # zoom in, verse blooms
    save(f, os.path.join(out, "05_cuddle_embrace.png"))
    print(f"  cuddle_blend={act1._cuddle_blend:.2f} zoom={engine.render_zoom:.2f} "
          f"bond={act1.oxytocin.value:.0f} verse_idx={act1._verse_idx}")

    # 5) STORM OF SHADOWS — force one; test failing to anchor (Mahi dims)
    fake.hold()                                    # let go of embrace
    for _ in range(40): f = step(engine, fake)
    act1._storm_active = STORM_LENGTH
    fake.hold("move_right")                        # NOT resting → unshielded
    for _ in range(150): f = step(engine, fake)
    dim_light = act1.companion.light
    save(f, os.path.join(out, "06_storm_unshielded.png"))

    # then ANCHOR correctly
    act1._storm_active = STORM_LENGTH
    fake.hold("rest")
    for _ in range(60): f = step(engine, fake)
    save(f, os.path.join(out, "07_storm_anchored.png"))
    print(f"  storm: mahi.light dimmed to {dim_light:.2f}, player.frozen={act1.player.frozen}, "
          f"mahi.pressing={act1.companion.pressing}")

    # 6) ACT 2 — Sunken Kingdom of the Oracles
    from states.act2_swamp import Act2SwampState
    fake.hold()
    engine.render_zoom = 1.0
    engine.state_mgr.replace(Act2SwampState(engine))
    for _ in range(60): f = step(engine, fake)
    save(f, os.path.join(out, "08_act2_swamp.png"))
    print(f"  state={type(engine.state_mgr.current).__name__}")

    print("\nExecution complete — all states & mechanics rendered.")
    pygame.quit()


if __name__ == "__main__":
    main()
