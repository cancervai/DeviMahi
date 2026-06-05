/* ============================================================
   easter-eggs.js — heart-trail cursor, konami code, "love"
   typing trigger, and shared FX helpers (toast + emoji burst).
   Exposes window.FX = { toast, burst, addLove }.
   ============================================================ */
(function () {
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- toast ---------- */
  const toastEl = document.getElementById('toast');
  let toastTimer;
  function toast(msg, ms) {
    if (!toastEl) return;
    toastEl.textContent = msg;
    toastEl.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toastEl.classList.remove('show'), ms || 2600);
  }

  /* ---------- emoji burst (confetti-ish) ---------- */
  function burst(x, y, emojis, count) {
    if (reduce) return;
    emojis = emojis || ['💛', '🌸', '🌷', '✨', '💐'];
    count = count || 18;
    for (let i = 0; i < count; i++) {
      const el = document.createElement('span');
      el.className = 'burst-piece';
      el.textContent = emojis[(Math.random() * emojis.length) | 0];
      el.style.left = x + 'px';
      el.style.top = y + 'px';
      document.body.appendChild(el);
      const ang = Math.random() * Math.PI * 2;
      const vel = 60 + Math.random() * 160;
      const dx = Math.cos(ang) * vel;
      const dy = Math.sin(ang) * vel - 120;
      const rot = (Math.random() * 720 - 360) + 'deg';
      el.animate([
        { transform: 'translate(0,0) rotate(0)', opacity: 1 },
        { transform: `translate(${dx}px,${dy + 240}px) rotate(${rot})`, opacity: 0 }
      ], { duration: 1100 + Math.random() * 700, easing: 'cubic-bezier(.2,.7,.3,1)' })
        .onfinish = () => el.remove();
    }
  }

  /* ---------- heart-trail cursor ---------- */
  const canvas = document.getElementById('heartTrail');
  if (canvas && !reduce) {
    const ctx = canvas.getContext('2d');
    let W, H, dpr = Math.min(devicePixelRatio || 1, 2);
    const hearts = [];
    function resize() {
      W = canvas.width = innerWidth * dpr;
      H = canvas.height = innerHeight * dpr;
      canvas.style.width = innerWidth + 'px';
      canvas.style.height = innerHeight + 'px';
    }
    resize(); addEventListener('resize', resize);
    let last = 0;
    addEventListener('pointermove', (e) => {
      const now = performance.now();
      if (now - last < 38) return;          // throttle
      last = now;
      hearts.push({ x: e.clientX * dpr, y: e.clientY * dpr, life: 1, s: (8 + Math.random() * 8) * dpr, vy: -0.3 * dpr });
      if (hearts.length > 40) hearts.shift();
    }, { passive: true });

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
      for (let i = hearts.length - 1; i >= 0; i--) {
        const h = hearts[i];
        h.life -= 0.02; h.y += h.vy;
        if (h.life <= 0) { hearts.splice(i, 1); continue; }
        heart(h.x, h.y, h.s, h.life);
      }
      requestAnimationFrame(draw);
    })();
  }

  /* ---------- konami code ---------- */
  const KONAMI = ['ArrowUp','ArrowUp','ArrowDown','ArrowDown','ArrowLeft','ArrowRight','ArrowLeft','ArrowRight','b','a'];
  let kIdx = 0;
  /* ---------- type "love" anywhere ---------- */
  let typed = '';

  addEventListener('keydown', (e) => {
    // konami
    if (e.key === KONAMI[kIdx]) {
      kIdx++;
      if (kIdx === KONAMI.length) { kIdx = 0; konamiParty(); }
    } else {
      kIdx = (e.key === KONAMI[0]) ? 1 : 0;
    }
    // love trigger
    if (/^[a-z]$/i.test(e.key)) {
      typed = (typed + e.key.toLowerCase()).slice(-4);
      if (typed === 'love') {
        typed = '';
        burst(innerWidth / 2, innerHeight / 2, ['💛','❤️','🌹','💐','✨'], 30);
        toast('I love you too, Mahi. Infinitely. 💛');
      }
    }
  });

  function konamiParty() {
    toast('🎉 KONAMI! you found the secret goddess buff: +999 charisma (you already had it)');
    if (window.Petals) window.Petals.rain(120);
    const cx = innerWidth / 2;
    for (let i = 0; i < 5; i++) {
      setTimeout(() => burst(cx + (i - 2) * 80, innerHeight * 0.4, ['👑','🌸','💛','✨','🦋'], 20), i * 160);
    }
  }

  window.FX = { toast, burst };
})();
