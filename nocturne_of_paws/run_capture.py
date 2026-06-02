"""
Headless execution harness — drives the engine through its states and saves
real rendered frames as PNGs so the game can be verified without a display.
"""
import sys, os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import pygame
pygame.init()
pygame.display.set_mode((320, 180))

from core.engine import Engine
from states.act1_citadel import Act1CitadelState
from states.waltz_minigame import WaltzMinigameState


class FakeInput:
    """Minimal input stub to drive states deterministically."""
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


def upscale_save(canvas, path, scale=4):
    big = pygame.transform.scale(canvas, (320 * scale, 180 * scale))
    pygame.image.save(big, path)
    print(f"  saved {path}")


def render(engine, frames, fake, dt=1/60):
    for _ in range(frames):
        engine.canvas.fill((42, 6, 12))
        engine.state_mgr.update(dt)
        engine.state_mgr.draw(engine.canvas)
        fake.clear()


def main():
    out = os.path.join(os.path.dirname(__file__), "screenshots")
    os.makedirs(out, exist_ok=True)

    engine = Engine()
    fake = FakeInput()
    engine.input = fake
    print(f"Engine up. scale={engine.scale} canvas={engine.canvas.get_size()}")

    # 1) MAIN MENU — let candle animation breathe a few frames
    render(engine, 30, fake)
    upscale_save(engine.canvas, os.path.join(out, "01_main_menu.png"))
    print(f"  state={type(engine.state_mgr.current).__name__}")

    # 2) ACT 1 CITADEL — enter directly, advance dialogue, walk Masum right
    engine.state_mgr.replace(Act1CitadelState(engine))
    render(engine, 10, fake)
    fake.press("interact"); render(engine, 1, fake)   # advance line 1
    fake.press("interact"); render(engine, 1, fake)   # advance line 2
    fake.hold("move_right", "run")
    render(engine, 90, fake)                            # run right ~1.5s
    upscale_save(engine.canvas, os.path.join(out, "02_act1_citadel.png"))
    px = engine.state_mgr.current.player.rect.x
    print(f"  state={type(engine.state_mgr.current).__name__}  masum.x={px}")

    # jump test
    fake.hold("move_right"); fake.press("jump"); render(engine, 1, fake)
    fake.hold("move_right"); render(engine, 20, fake)
    upscale_save(engine.canvas, os.path.join(out, "03_act1_jump.png"))

    # 3) WALTZ MINIGAME — push state, let beats spawn, simulate on-beat taps
    fake.hold(); engine.state_mgr.push(WaltzMinigameState(engine))
    render(engine, 40, fake)
    for _ in range(8):
        fake.press("move_left", "move_right", "move_up", "move_down")
        render(engine, 1, fake)
        render(engine, 12, fake)
    upscale_save(engine.canvas, os.path.join(out, "04_waltz_minigame.png"))
    wz = engine.state_mgr.current
    print(f"  state={type(wz).__name__}  score={wz._score} combo={wz._combo}")

    print("\nExecution complete — all states rendered successfully.")
    pygame.quit()


if __name__ == "__main__":
    main()
