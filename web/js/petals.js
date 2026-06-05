/* ============================================================
   petals.js — falling sakura/rose petals.  Reacts to mouse on
   desktop, to touch on phones.  iOS Safari 12 safe (no Pointer
   Events).  Tuned light for iPhone 6 Plus (A8).  window.Petals.
   ============================================================ */
(function () {
  var canvas = document.getElementById('petals');
  if (!canvas) return;
  var ctx = canvas.getContext('2d');
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var coarse = window.matchMedia('(pointer: coarse)').matches;

  var W = 0, H = 0, dpr = Math.min(window.devicePixelRatio || 1, 2);
  var mouse = { x: -999, y: -999 };
  var COLORS = ['#e79bb0', '#f4c2cf', '#e9b949', '#ffe1a8', '#f7d9e2', '#cde9c4'];

  function resize() {
    W = canvas.width = window.innerWidth * dpr;
    H = canvas.height = window.innerHeight * dpr;
    canvas.style.width = window.innerWidth + 'px';
    canvas.style.height = window.innerHeight + 'px';
  }
  resize();
  window.addEventListener('resize', resize);

  // base count scales with viewport; light on phones / reduced motion
  var baseCount = reduce ? 8 : (coarse ? 18 : (window.innerWidth < 640 ? 22 : 46));

  function rnd(a, b) { return a + Math.random() * (b - a); }

  function Petal(initial) { this.reset(initial); }
  Petal.prototype.reset = function (initial) {
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
  };
  Petal.prototype.step = function (t) {
    this.x += this.vx + Math.sin(t * 0.001 + this.swayOff) * this.sway * dpr;
    this.y += this.vy;
    this.rot += this.spin;
    var dx = this.x - mouse.x, dy = this.y - mouse.y;
    var d2 = dx * dx + dy * dy;
    var R = 110 * dpr;
    if (d2 < R * R) {
      var d = Math.sqrt(d2) || 1;
      var f = (1 - d / R) * 2.4 * dpr;
      this.x += (dx / d) * f;
      this.y += (dy / d) * f;
    }
    if (this.y > H + 20 || this.x < -40 || this.x > W + 40) this.reset(false);
  };
  Petal.prototype.draw = function () {
    ctx.save();
    ctx.translate(this.x, this.y);
    ctx.rotate(this.rot);
    ctx.globalAlpha = this.alpha;
    ctx.fillStyle = this.color;
    ctx.beginPath();
    ctx.moveTo(0, -this.r);
    ctx.bezierCurveTo(this.r, -this.r * 0.5, this.r * 0.6, this.r, 0, this.r);
    ctx.bezierCurveTo(-this.r * 0.6, this.r, -this.r, -this.r * 0.5, 0, -this.r);
    ctx.fill();
    ctx.restore();
  };

  var petals = [];
  for (var i = 0; i < baseCount; i++) petals.push(new Petal(true));
  var extra = [];

  // mouse (desktop) + touch (phones) drive the repulsion point
  window.addEventListener('mousemove', function (e) { mouse.x = e.clientX * dpr; mouse.y = e.clientY * dpr; });
  window.addEventListener('mouseout', function () { mouse.x = mouse.y = -999; });
  window.addEventListener('touchmove', function (e) {
    if (e.touches && e.touches[0]) { mouse.x = e.touches[0].clientX * dpr; mouse.y = e.touches[0].clientY * dpr; }
  });
  window.addEventListener('touchend', function () { mouse.x = mouse.y = -999; });

  var running = true;
  function loop(t) {
    if (!running) return;
    ctx.clearRect(0, 0, W, H);
    var p, j;
    for (j = 0; j < petals.length; j++) { p = petals[j]; p.step(t); p.draw(); }
    for (j = extra.length - 1; j >= 0; j--) {
      p = extra[j];
      p.step(t); p.draw();
      p.life -= 1;
      if (p.life <= 0 || p.y > H + 20) extra.splice(j, 1);
    }
    requestAnimationFrame(loop);
  }
  requestAnimationFrame(loop);

  function rain(n) {
    n = n || 60;
    if (coarse) n = Math.min(n, 60);
    for (var k = 0; k < n; k++) {
      var p = new Petal(false);
      p.y = rnd(-H * 0.3, 0);
      p.vy = rnd(1.5, 3.5) * dpr;
      p.life = 600;
      extra.push(p);
    }
  }

  document.addEventListener('visibilitychange', function () {
    running = !document.hidden;
    if (running) requestAnimationFrame(loop);
  });

  window.Petals = { rain: rain };
})();
