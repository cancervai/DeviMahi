/* ============================================================
   petals.js — falling sakura/rose petals that react to cursor.
   Lightweight canvas particle system. Exposes window.Petals.
   ============================================================ */
(function () {
  const canvas = document.getElementById('petals');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  let W = 0, H = 0, dpr = Math.min(window.devicePixelRatio || 1, 2);
  const mouse = { x: -999, y: -999 };
  const COLORS = ['#e79bb0', '#f4c2cf', '#e9b949', '#ffe1a8', '#f7d9e2', '#cde9c4'];

  function resize() {
    W = canvas.width = innerWidth * dpr;
    H = canvas.height = innerHeight * dpr;
    canvas.style.width = innerWidth + 'px';
    canvas.style.height = innerHeight + 'px';
  }
  resize();
  addEventListener('resize', resize);

  // base count scales with viewport; fewer on mobile / reduced motion
  const baseCount = reduce ? 10 : (innerWidth < 640 ? 26 : 48);

  function rnd(a, b) { return a + Math.random() * (b - a); }

  class Petal {
    constructor(initial) {
      this.reset(initial);
    }
    reset(initial) {
      this.x = rnd(0, W);
      this.y = initial ? rnd(0, H) : rnd(-H * 0.2, -10);
      this.r = rnd(5, 12) * dpr;
      this.vy = rnd(0.4, 1.4) * dpr;
      this.vx = rnd(-0.4, 0.4) * dpr;
      this.spin = rnd(-0.04, 0.04);
      this.rot = rnd(0, Math.PI * 2);
      this.color = COLORS[(Math.random() * COLORS.length) | 0];
      this.sway = rnd(0.4, 1.2);
      this.swayOff = rnd(0, Math.PI * 2);
      this.alpha = rnd(0.55, 0.95);
    }
    step(t) {
      this.x += this.vx + Math.sin(t * 0.001 + this.swayOff) * this.sway * dpr;
      this.y += this.vy;
      this.rot += this.spin;
      // gentle cursor repulsion
      const dx = this.x - mouse.x, dy = this.y - mouse.y;
      const d2 = dx * dx + dy * dy;
      const R = 120 * dpr;
      if (d2 < R * R) {
        const d = Math.sqrt(d2) || 1;
        const f = (1 - d / R) * 2.4 * dpr;
        this.x += (dx / d) * f;
        this.y += (dy / d) * f;
      }
      if (this.y > H + 20 || this.x < -40 || this.x > W + 40) this.reset(false);
    }
    draw() {
      ctx.save();
      ctx.translate(this.x, this.y);
      ctx.rotate(this.rot);
      ctx.globalAlpha = this.alpha;
      ctx.fillStyle = this.color;
      // petal = pinched ellipse
      ctx.beginPath();
      ctx.moveTo(0, -this.r);
      ctx.bezierCurveTo(this.r, -this.r * 0.5, this.r * 0.6, this.r, 0, this.r);
      ctx.bezierCurveTo(-this.r * 0.6, this.r, -this.r, -this.r * 0.5, 0, -this.r);
      ctx.fill();
      ctx.restore();
    }
  }

  let petals = Array.from({ length: baseCount }, () => new Petal(true));
  let extra = [];   // temporary burst petals for "make it rain"

  addEventListener('pointermove', (e) => { mouse.x = e.clientX * dpr; mouse.y = e.clientY * dpr; }, { passive: true });
  addEventListener('pointerleave', () => { mouse.x = mouse.y = -999; });

  let running = true;
  function loop(t) {
    if (!running) return;
    ctx.clearRect(0, 0, W, H);
    for (const p of petals) { p.step(t); p.draw(); }
    for (let i = extra.length - 1; i >= 0; i--) {
      const p = extra[i];
      p.step(t); p.draw();
      p.life -= 1;
      if (p.life <= 0 || p.y > H + 20) extra.splice(i, 1);
    }
    requestAnimationFrame(loop);
  }
  requestAnimationFrame(loop);

  // public: burst a wave of petals from the top (the "make it rain" button)
  function rain(n) {
    n = n || 60;
    for (let i = 0; i < n; i++) {
      const p = new Petal(false);
      p.y = rnd(-H * 0.3, 0);
      p.vy = rnd(1.5, 3.5) * dpr;
      p.life = 600;
      extra.push(p);
    }
  }

  document.addEventListener('visibilitychange', () => {
    running = !document.hidden;
    if (running) requestAnimationFrame(loop);
  });

  window.Petals = { rain };
})();
