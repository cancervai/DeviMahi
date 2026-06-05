/* ============================================================
   main.js — loader, bouquet, shrine, the little game, audio,
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
      ['🥀', "i think about your mouth more than i'll ever admit in writing."],
      ['🌹', "your laugh walks into the room and undresses my bad mood."],
      ['🖤', "i'd cancel plans, gods, and whole timelines just to watch you breathe."],
      ['🌙', "you're the only prayer i say with my eyes open."],
      ['🍷', "some nights i just want to ruin your lipstick. respectfully. mostly."],
      ['🐈‍⬛', "you call me your evil spirit, then wonder why i won't leave. i live here now."],
      ['🔥', "i behave in public so i can misbehave with you in private."],
      ['🌑', "you make 'come over' sound like scripture, and i'm a devout man."],
      ['💋', "i'm not clingy. you're just better than oxygen and i'd like to breathe."],
      ['🥀', "you, me, no plans, the lights low — that's the whole poem."],
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
      FX.burst(r.left + r.width / 2, r.top, ['🖤', '🥀', '🌙', '✨', '🦶'], 16);
      const lines = [
        'noted. the feet acknowledge your devotion. 🖤',
        'you kneel suspiciously well. we don\'t ask questions here.',
        'ten toes blessed you back. allegedly with their tongue.',
        'another knee sacrificed to a worthy, worthy cause.'
      ];
      FX.toast(lines[n % lines.length]);
    });
    function render() {
      if (out) out.innerHTML = 'Devotees who have bowed: <b>' + n + '</b>';
    }
  })();

  /* ============================================================
     3 · THE LITTLE GAME — catch-the-hearts mini-game
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
      basket.style.webkitTransform = 'translateX(-50%)';
      basket.style.transform = 'translateX(-50%)';
    }
    // mouse (desktop) + touch (phones); iOS Safari 12 has no Pointer Events
    arena.addEventListener('mousemove', (e) => moveBasket(e.clientX), { passive: true });
    arena.addEventListener('touchmove', (e) => { if (e.touches[0]) moveBasket(e.touches[0].clientX); }, { passive: true });

    startBtn && startBtn.addEventListener('click', () => playing ? null : start());

    function start() {
      playing = true; startBtn.textContent = 'catching… 🖤';
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
        el.style.webkitTransform = `translateY(${y}px)`;
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
      startBtn.textContent = 'all yours 🖤';
      if (secret) { secret.hidden = false; secret.scrollIntoView({ behavior: 'smooth', block: 'center' }); }
      FX.toast('full. you filled it without even trying — you\'ve been doing that to me since night one. 🖤');
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
     5 · "HERE'S WHAT I'M THINKING RN" (floating button, injected)
     ============================================================ */
  (function thinking() {
    const lines = [
      "thinking about your collarbones again. anyway — how was your day.",
      "wondering if you're wearing the thing i like. no reason.",
      "i could be productive. or i could think about your thighs. it isn't close.",
      "composing a very respectful poem about the small of your back.",
      "you crossed my mind. you usually do. you also usually stay a while.",
      "imagining you in my hoodie and nothing else makes a sound in my head.",
      "50% missing you, 50% plotting, 100% yours.",
      "we should cancel tonight. i have a proposal. it's just you.",
      "your neck. that's the whole thought. that's it.",
      "was being normal, then remembered you exist. ruined. happily."
    ];
    const btn = document.createElement('button');
    btn.id = 'thinkingBtn';
    btn.textContent = "here's what i'm thinking rn 🐈‍⬛";
    Object.assign(btn.style, {
      position: 'fixed', left: '14px', bottom: '14px', zIndex: 50,
      fontFamily: 'Quicksand, sans-serif', fontWeight: 700, fontSize: '.82rem',
      color: '#fbeef3', border: '1px solid rgba(255,255,255,.12)', cursor: 'pointer',
      padding: '.7rem 1rem', borderRadius: '99px', maxWidth: '70vw',
      background: 'linear-gradient(120deg,#8a3158,#bd9540)',
      boxShadow: '0 8px 22px rgba(0,0,0,.5)', WebkitAppearance: 'none'
    });
    btn.addEventListener('click', () => {
      const msg = lines[(Math.random() * lines.length) | 0];
      FX.toast(msg, 3600);
      const r = btn.getBoundingClientRect();
      FX.burst(r.left + r.width / 2, r.top, ['🖤', '🥀', '🌙'], 10);
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
      FX.burst(r.left + r.width / 2, r.top, ['🥀', '🌹', '🖤', '🌙'], 24);
      FX.toast('🥀 for you. and the version of you in every dark i\'ve imagined.');
    });
    replayBtn && replayBtn.addEventListener('click', () => {
      if (window.__lenis) window.__lenis.scrollTo(0, { duration: 2 });
      else window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  })();
})();
