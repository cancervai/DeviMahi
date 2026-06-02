"""
State manager: push/pop stack of game states with clean enter/exit hooks.
"""


class StateManager:
    def __init__(self, engine):
        self.engine = engine
        self._stack = []

    # ── Stack operations ──────────────────────────────────────────────────────

    def push(self, state):
        if self._stack:
            self._stack[-1].on_pause()
        self._stack.append(state)
        state.on_enter()

    def pop(self):
        if not self._stack:
            return
        leaving = self._stack.pop()
        leaving.on_exit()
        if self._stack:
            self._stack[-1].on_resume()

    def replace(self, state):
        """Pop current state and push a new one (no resume for previous)."""
        if self._stack:
            leaving = self._stack.pop()
            leaving.on_exit()
        self._stack.append(state)
        state.on_enter()

    # ── Loop delegation ───────────────────────────────────────────────────────

    def update(self, dt):
        if self._stack:
            self._stack[-1].update(dt)

    def draw(self, surface):
        # Draw all states bottom-to-top (allows transparent overlay states)
        for state in self._stack:
            state.draw(surface)

    @property
    def current(self):
        return self._stack[-1] if self._stack else None
