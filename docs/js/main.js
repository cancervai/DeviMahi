/* ============================================================
   main.js — loader, bouquet, shrine, serotonin game, audio,
   compliments, finale controls.  DeviMahi 🌸
   ============================================================ */
(function () {
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const FX = window.FX || { toast(){}, burst(){} };

  /* ============================================================
     0 · LOADER
     ============================================================ */
  (function loader() {
    const el = document.getElementById('loader');
    const fill = document.getElementById('loaderFill');
    const pct = document.getElementById('loaderPct');
    if (!el) return;
    let p = 0;
    const target = () => (document.readyState === 'complete' ? 100 : 88);
    const iv = setInterval(() => {
      p += Math.max(1, (target() - p) * 0.08);
      if (p > target()) p = target();
      const v = Math.round(p);
      if (fill) fill.style.width = v + '%';
      if (pct) pct.textContent = v + '%';
      if (v >= 100) { clearInterval(iv); done(); }
    }, 60);
    function done() {
      setTimeout(() => {
        el.classList.add('done');
        if (window.__lenis) window.__lenis.scrollTo(0, { immediate: true });
      }, 350);
    }
    // safety: never trap the user behind the loader
    setTimeout(() => { if (!el.classList.contains('done')) { p = 100; el.classList.add('done'); } }, 6000);
  })();

  /* ============================================================
     1 · INTERACTIVE BOUQUET OF REASONS
     ============================================================ */
  (function bouquet() {
    const wrap = document.getElementById('bouquet');
    const bubble = document.getElementById('reasonBubble');
    if (!wrap) return;

    const REASONS = [
      ['🌷', "Your laugh resets my entire nervous system. 0 to serotonin in one second."],
      ['🌸', "You're so cute it's frankly a safety hazard. I've filed reports."],
      ['🌹', "You make 'home' a person, not a place. Specifically: you."],
      ['🌻', "When you're happy, the whole room gets a software update."],
      ['🌼', "You're the calm AND the butterflies. Pick a lane — actually no, keep both."],
      ['💐', "I'd cross any swamp, fight any frog, for one of your smiles. (game reference, iykyk)"],
      ['🪻', "Your kindness could end wars. Goddess of Peace was NOT an exaggeration."],
      ['🌺', "You hold kittens like a Ghibli protagonist and my heart like it's nothing."],
      ['🏵️', "Even your worst days are better company than anyone's best."],
      ['🌷', "You + me = the only equation I ever want to solve. Forever."],
    ];

    const headColors = ['#e79bb0', '#e9b949', '#f4c2cf', '#c96a86', '#f0a6c0', '#ffd27a'];
    // bouquet-ish positions (percent of container)
    const spots = [
      [50, 16], [33, 24], [67, 24], [22, 40], [50, 38], [78, 40],
      [33, 56], [67, 56], [44, 70], [58, 70]
    ];

    REASONS.forEach((r, i) => {
      const [emoji, text] = r;
      const [x, y] = spots[i % spots.length];
      const f = document.createElement('button');
      f.className = 'flower';
      f.style.left = x + '%';
      f.style.top = y + '%';
      f.setAttribute('aria-label', 'A reason: ' + text);
      const col = headColors[i % headColors.length];
      f.innerHTML = flowerSVG(col);
      f.addEventListener('click', (e) => {
        showReason(emoji, text);
        const rect = e.currentTarget.getBoundingClientRect();
        FX.burst(rect.left + rect.width / 2, rect.top + rect.height / 2, ['💛', emoji, '✨'], 12);
      });
      wrap.appendChild(f);
    });

    function showReason(emoji, text) {
      if (!bubble) return;
      bubble.querySelector('.rb-emoji').textContent = emoji;
      bubble.querySelector('.rb-text').textContent = text;
      bubble.classList.remove('bump'); void bubble.offsetWidth; bubble.classList.add('bump');
    }

    // bloom flowers when the chapter scrolls into view
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => {
        if (en.isIntersecting) {
          const flowers = wrap.querySelectorAll('.flower');
          flowers.forEach((fl, idx) => setTimeout(() => fl.classList.add('bloomed'), idx * 110));
          io.disconnect();
        }
      });
    }, { threshold: 0.25 });
    io.observe(wrap);

    function flowerSVG(color) {
      return `<svg viewBox="0 0 80 80" aria-hidden="true">
        <path class="stem" d="M40 78 C40 60 40 52 40 44"/>
        <path class="stem" d="M40 60 C32 56 28 50 26 46"/>
        <path class="stem" d="M40 56 C48 52 52 48 54 44"/>
        <g class="head">
          ${[0,72,144,216,288].map(a=>`<ellipse cx="40" cy="22" rx="9" ry="15" fill="${color}" transform="rotate(${a} 40 36)"/>`).join('')}
          <circle cx="40" cy="36" r="8" fill="#e9b949"/>
        </g>
      </svg>`;
    }
  })();

  /* ============================================================
     2 · SHRINE — bow counter
     ============================================================ */
  (function shrine() {
    const btn = document.getElementById('bowBtn');
    const out = document.getElementById('bowCount');
    if (!btn) return;
    let n = parseInt(localStorage.getItem('mahi_bows') || '0', 10);
    render();
    btn.addEventListener('click', (e) => {
      n++;
      localStorage.setItem('mahi_bows', String(n));
      render();
      const r = e.currentTarget.getBoundingClientRect();
      FX.burst(r.left + r.width / 2, r.top, ['🛐', '👑', '🌹', '✨', '🦶'], 16);
      const lines = [
        'Devotion recorded. The feet have noted your loyalty. 🙏',
        'Blessed. You may now ascend 0.2 cm spiritually.',
        'The Holy Feet are pleased. Continue.',
        'Your knees are sacrificed for a noble cause.'
      ];
      FX.toast(lines[n % lines.length]);
    });
    function render() {
      if (out) out.innerHTML = 'Devotees who have bowed: <b>' + n + '</b>';
    }
  })();

  /* ============================================================
     3 · SEROTONIN STATION — catch-the-hearts mini-game
     ============================================================ */
  (function game() {
    const arena = document.getElementById('gameArena');
    const basket = document.getElementById('basket');
    const scoreEl = document.getElementById('gameScore');
    const startBtn = document.getElementById('gameStart');
    const secret = document.getElementById('gameSecret');
    if (!arena || !basket) return;

    let score = 0, playing = false, spawnTimer = null, items = [], raf = null;
    const GOOD = ['💛', '🌸', '🌷', '💐', '🦋', '🌹'];

    // basket follows pointer / touch within arena
    function moveBasket(clientX) {
      const r = arena.getBoundingClientRect();
      let x = clientX - r.left;
      x = Math.max(28, Math.min(r.width - 28, x));
      basket.style.left = x + 'px';
      basket.style.transform = 'translateX(-50%)';
    }
    arena.addEventListener('pointermove', (e) => moveBasket(e.clientX), { passive: true });
    arena.addEventListener('touchmove', (e) => { if (e.touches[0]) moveBasket(e.touches[0].clientX); }, { passive: true });

    startBtn && startBtn.addEventListener('click', () => playing ? null : start());

    function start() {
      playing = true; startBtn.textContent = 'Catching… 💘';
      spawn();
      loop();
    }
    function spawn() {
      if (!playing) return;
      const el = document.createElement('span');
      el.className = 'fall';
      el.textContent = GOOD[(Math.random() * GOOD.length) | 0];
      const r = arena.getBoundingClientRect();
      const x = 24 + Math.random() * (r.width - 48);
      el.style.left = x + 'px';
      el.dataset.x = x;
      el.dataset.y = -40;
      el.dataset.v = (1.8 + Math.random() * 2.2);
      arena.appendChild(el);
      items.push(el);
      spawnTimer = setTimeout(spawn, reduce ? 900 : 620);
    }
    function loop() {
      if (!playing) return;
      const r = arena.getBoundingClientRect();
      const bx = parseFloat(basket.style.left || r.width / 2);
      const by = r.height - 40;
      for (let i = items.length - 1; i >= 0; i--) {
        const el = items[i];
        let y = parseFloat(el.dataset.y) + parseFloat(el.dataset.v);
        el.dataset.y = y;
        el.style.transform = `translateY(${y}px)`;
        const x = parseFloat(el.dataset.x);
        if (y > by - 24 && y < by + 30 && Math.abs(x - bx) < 46) {
          catchItem(el, i); continue;
        }
        if (y > r.height + 40) { el.remove(); items.splice(i, 1); }
      }
      raf = requestAnimationFrame(loop);
    }
    function catchItem(el, i) {
      const r = el.getBoundingClientRect();
      FX.burst(r.left + 12, r.top + 12, ['✨', '💛'], 6);
      el.remove(); items.splice(i, 1);
      score = Math.min(100, score + 7);
      if (scoreEl) scoreEl.textContent = score;
      if (score >= 100) win();
    }
    function win() {
      playing = false;
      clearTimeout(spawnTimer);
      cancelAnimationFrame(raf);
      items.forEach(el => el.remove()); items = [];
      startBtn.textContent = 'Maxed out 💛';
      if (secret) { secret.hidden = false; secret.scrollIntoView({ behavior: 'smooth', block: 'center' }); }
      FX.toast('100%! You filled the meter AND my heart. 💛');
      if (window.Petals) window.Petals.rain(80);
    }
  })();

  /* ============================================================
     4 · AUDIO — gentle WebAudio music-box (no asset needed)
     ============================================================ */
  (function audio() {
    const btn = document.getElementById('audioToggle');
    if (!btn) return;
    let ctxA = null, gain = null, timer = null, on = false;
    // a soft, dreamy pentatonic loop (Hz)
    const NOTES = [523.25, 587.33, 659.25, 783.99, 880.0, 783.99, 659.25, 587.33];
    let step = 0;

    function ensure() {
      if (ctxA) return;
      const AC = window.AudioContext || window.webkitAudioContext;
      if (!AC) return;
      ctxA = new AC();
      gain = ctxA.createGain();
      gain.gain.value = 0.0;
      gain.connect(ctxA.destination);
    }
    function note(freq) {
      const o = ctxA.createOscillator();
      const g = ctxA.createGain();
      o.type = 'sine';
      o.frequency.value = freq;
      const t = ctxA.currentTime;
      g.gain.setValueAtTime(0, t);
      g.gain.linearRampToValueAtTime(0.18, t + 0.04);
      g.gain.exponentialRampToValueAtTime(0.001, t + 1.6);
      o.connect(g); g.connect(gain);
      o.start(t); o.stop(t + 1.7);
      // soft octave shimmer
      const o2 = ctxA.createOscillator();
      const g2 = ctxA.createGain();
      o2.type = 'triangle'; o2.frequency.value = freq * 2;
      g2.gain.setValueAtTime(0, t);
      g2.gain.linearRampToValueAtTime(0.05, t + 0.04);
      g2.gain.exponentialRampToValueAtTime(0.001, t + 1.2);
      o2.connect(g2); g2.connect(gain);
      o2.start(t); o2.stop(t + 1.3);
    }
    function startLoop() {
      ensure();
      if (!ctxA) { FX.toast('Your browser declined the music box 🥲'); return; }
      ctxA.resume();
      gain.gain.linearRampToValueAtTime(0.6, ctxA.currentTime + 0.6);
      const tick = () => { note(NOTES[step % NOTES.length]); step++; };
      tick();
      timer = setInterval(tick, 900);
      on = true;
      btn.querySelector('.audio-ico').textContent = '🔊';
      btn.title = 'Music (on)';
    }
    function stopLoop() {
      if (timer) clearInterval(timer);
      if (gain && ctxA) gain.gain.linearRampToValueAtTime(0.0, ctxA.currentTime + 0.4);
      on = false;
      btn.querySelector('.audio-ico').textContent = '🔇';
      btn.title = 'Music (off)';
    }
    btn.addEventListener('click', () => on ? stopLoop() : startLoop());
  })();

  /* ============================================================
     5 · COMPLIMENT GENERATOR (floating button, injected)
     ============================================================ */
  (function compliments() {
    const lines = [
      "Scientific fact: you're the prettiest person to ever exist. Peer-reviewed by me.",
      "If loving you were a job, I'd work unpaid overtime forever. 💼",
      "You're 90% sunshine, 10% chaos, and 100% mine. Math checks out.",
      "Warning: prolonged eye contact with Mahi may cause permanent happiness.",
      "You make my heart do that dumb little flip. Every. Single. Time.",
      "Goddess of Love & Peace? Babe, you're overqualified.",
      "I'd choose you in every lifetime, even the ones where I'm a frog. 🐸",
      "You + a bouquet = redundant. You ARE the bouquet.",
      "On a scale of 1 to 10, you're an entire ecosystem of cuteness.",
      "Plot twist: I was the lucky one all along. 💛"
    ];
    const btn = document.createElement('button');
    btn.id = 'complimentBtn';
    btn.textContent = '✨ Need a compliment?';
    Object.assign(btn.style, {
      position: 'fixed', left: '14px', bottom: '14px', zIndex: 50,
      fontFamily: 'Quicksand, sans-serif', fontWeight: 700, fontSize: '.85rem',
      color: '#fff', border: 'none', cursor: 'pointer', padding: '.7rem 1rem',
      borderRadius: '99px', background: 'linear-gradient(120deg,#c96a86,#caa033)',
      boxShadow: '0 8px 20px rgba(74,59,70,.25)'
    });
    btn.addEventListener('click', (e) => {
      const msg = lines[(Math.random() * lines.length) | 0];
      FX.toast(msg, 3400);
      const r = btn.getBoundingClientRect();
      FX.burst(r.left + r.width / 2, r.top, ['✨', '💛', '🌸'], 10);
    });
    document.body.appendChild(btn);
  })();

  /* ============================================================
     6 · FINALE controls
     ============================================================ */
  (function finale() {
    const rainBtn = document.getElementById('rainBtn');
    const replayBtn = document.getElementById('replayBtn');
    rainBtn && rainBtn.addEventListener('click', (e) => {
      if (window.Petals) window.Petals.rain(120);
      const r = e.currentTarget.getBoundingClientRect();
      FX.burst(r.left + r.width / 2, r.top, ['🌹', '🌸', '💐', '💛'], 24);
      FX.toast('🌹 for you. and you. and also you. all of you, Mahi.');
    });
    replayBtn && replayBtn.addEventListener('click', () => {
      if (window.__lenis) window.__lenis.scrollTo(0, { duration: 2 });
      else window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  })();
})();
