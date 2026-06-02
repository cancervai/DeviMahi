"""
Abstract base class for all game states.
"""


class BaseState:
    def __init__(self, engine):
        self.engine    = engine
        self.state_mgr = engine.state_mgr
        self.input     = engine.input

    # ── Lifecycle hooks ───────────────────────────────────────────────────────

    def on_enter(self):  pass
    def on_exit(self):   pass
    def on_pause(self):  pass
    def on_resume(self): pass

    # ── Loop ─────────────────────────────────────────────────────────────────

    def update(self, dt: float):    pass
    def draw(self, surface):        pass
    def draw_overlay(self, surface): pass   # crisp HUD pass, drawn after zoom
