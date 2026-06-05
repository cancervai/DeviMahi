/* ============================================================
   easter-eggs.js — heart-trail cursor (desktop only), konami code,
   "love" typing trigger, and shared FX helpers (toast + emoji burst).
   iOS Safari 12 safe: no WAAPI (.animate), no optional chaining.
   Exposes window.FX = { toast, burst }.
   ============================================================ */
(function () {
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var coarse = window.matchMedia('(pointer: coarse)').matches; // phones/tablets

  /* ---------- toast ---------- */
  var toastEl = document.getElementById('toast');
  var toastTimer;
  function toast(msg, ms) {
    if (!toastEl) return;
    toastEl.textContent = msg;
    toastEl.className = 'toast show';
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toastEl.className = 'toast'; }, ms || 2600);
  }

  /* ---------- emoji burst (CSS-transition, Safari-12 safe) ---------- */
  function setTransform(el, v) { el.style.webkitTransform = v; el.style.transform = v; }
  function burst(x, y, emojis, count) {
    if (reduce) return;
    emojis = emojis || ['💛', '🌸', '🌷', '✨', '💐'];
    // fewer pieces on phones to keep the A8 GPU happy
    count = count || 18;
    if (coarse) count = Math.min(count, 10);
    for (var i = 0; i < count; i++) {
      (function () {
        var el = document.createElement('span');
        el.className = 'burst-piece';
        el.textContent = emojis[(Math.random() * emojis.length) | 0];
        el.style.left = x + 'px';
        el.style.top = y + 'px';
        setTransform(el, 'translate(0,0)');
        document.body.appendChild(el);
        var ang = Math.random() * Math.PI * 2;
        var vel = 60 + Math.random() * 150;
        var dx = Math.cos(ang) * vel;
        var dy = Math.sin(ang) * vel - 110;
        var rot = (Math.random() * 720 - 360);
        var dur = 1.1 + Math.random() * 0.6;
        el.style.webkitTransition = '-webkit-transform ' + dur + 's cubic-bezier(.2,.7,.3,1), opacity ' + dur + 's';
        el.style.transition = 'transform ' + dur + 's cubic-bezier(.2,.7,.3,1), opacity ' + dur + 's';
        // force a reflow so the transition runs from the start position
        /* eslint-disable no-unused-expressions */
        el.offsetHeight;
        requestAnimationFrame(function () {
          setTransform(el, 'translate(' + dx + 'px,' + (dy + 240) + 'px) rotate(' + rot + 'deg)');
          el.style.opacity = '0';
        });
        setTimeout(function () { if (el.parentNode) el.parentNode.removeChild(el); }, (dur * 1000) + 200);
      })();
    }
  }

  /* ---------- heart-trail cursor (desktop pointers only) ---------- */
  var canvas = document.getElementById('heartTrail');
  if (canvas && !reduce && !coarse) {
    var ctx = canvas.getContext('2d');
    var W, H, dpr = Math.min(window.devicePixelRatio || 1, 2);
    var hearts = [];
    function resize() {
      W = canvas.width = window.innerWidth * dpr;
      H = canvas.height = window.innerHeight * dpr;
      canvas.style.width = window.innerWidth + 'px';
      canvas.style.height = window.innerHeight + 'px';
    }
    resize();
    window.addEventListener('resize', resize);
    var last = 0;
    window.addEventListener('mousemove', function (e) {
      var now = (window.performance && performance.now) ? performance.now() : Date.now();
      if (now - last < 40) return;
      last = now;
      hearts.push({ x: e.clientX * dpr, y: e.clientY * dpr, life: 1, s: (8 + Math.random() * 8) * dpr, vy: -0.3 * dpr });
      if (hearts.length > 36) hearts.shift();
    });
    function heart(x, y, s, a) {
      ctx.save(); ctx.translate(x, y); ctx.scale(s / 16, s / 16); ctx.globalAlpha = a;
      ctx.fillStyle = '#e79bb0';
      ctx.beginPath();
      ctx.moveTo(0, 4);
      ctx.bezierCurveTo(-8, -6, -16, 4, 0, 16);
      ctx.bezierCurveTo(16, 4, 8, -6, 0, 4);
      ctx.fill(); ctx.restore();
    }
    (function draw() {
      ctx.clearRect(0, 0, W, H);
      for (var i = hearts.length - 1; i >= 0; i--) {
        var h = hearts[i];
        h.life -= 0.02; h.y += h.vy;
        if (h.life <= 0) { hearts.splice(i, 1); continue; }
        heart(h.x, h.y, h.s, h.life);
      }
      requestAnimationFrame(draw);
    })();
  }

  /* ---------- konami code ---------- */
  var KONAMI = ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'b', 'a'];
  var kIdx = 0;
  var typed = '';

  window.addEventListener('keydown', function (e) {
    if (e.key === KONAMI[kIdx]) {
      kIdx++;
      if (kIdx === KONAMI.length) { kIdx = 0; konamiParty(); }
    } else {
      kIdx = (e.key === KONAMI[0]) ? 1 : 0;
    }
    if (/^[a-z]$/i.test(e.key)) {
      typed = (typed + e.key.toLowerCase()).slice(-4);
      if (typed === 'love') {
        typed = '';
        burst(window.innerWidth / 2, window.innerHeight / 2, ['💛', '❤️', '🌹', '💐', '✨'], 30);
        toast('I love you too, Mahi. Infinitely. 💛');
      }
    }
  });

  function konamiParty() {
    toast('🎉 KONAMI! secret goddess buff unlocked: +999 charisma (you already had it)');
    if (window.Petals) window.Petals.rain(120);
    var cx = window.innerWidth / 2;
    for (var i = 0; i < 5; i++) {
      (function (i) {
        setTimeout(function () { burst(cx + (i - 2) * 80, window.innerHeight * 0.4, ['👑', '🌸', '💛', '✨', '🦋'], 18); }, i * 160);
      })(i);
    }
  }

  window.FX = { toast: toast, burst: burst };
})();
