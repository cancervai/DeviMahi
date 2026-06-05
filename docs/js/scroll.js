/* ============================================================
   scroll.js — Lenis smooth scroll + GSAP ScrollTrigger.
   Handles: reveals, parallax, hero title, typewriter, and the
   scroll-linked Oxytocin meter. Degrades gracefully if CDNs fail.
   ============================================================ */
(function () {
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const hasGSAP = typeof window.gsap !== 'undefined' && typeof window.ScrollTrigger !== 'undefined';

  // Fallback: if libs failed to load, just show everything.
  if (!hasGSAP) {
    document.querySelectorAll('.reveal').forEach(el => { el.style.opacity = 1; el.style.transform = 'none'; });
    setupOxytocinFallback();
    setupTypewriterFallback();
    return;
  }

  gsap.registerPlugin(ScrollTrigger);

  /* ---------- Lenis smooth scroll ---------- */
  let lenis = null;
  if (!reduce && typeof window.Lenis !== 'undefined') {
    lenis = new Lenis({ duration: 1.1, smoothWheel: true, lerp: 0.1 });
    lenis.on('scroll', ScrollTrigger.update);
    gsap.ticker.add((t) => lenis.raf(t * 1000));
    gsap.ticker.lagSmoothing(0);
    document.documentElement.classList.add('lenis');
    window.__lenis = lenis; // expose for replay/anchor scrolling
  }

  // smooth anchor jumps through Lenis when present
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', (e) => {
      const id = a.getAttribute('href');
      const target = document.querySelector(id);
      if (!target) return;
      e.preventDefault();
      if (lenis) lenis.scrollTo(target, { offset: 0, duration: 1.4 });
      else target.scrollIntoView({ behavior: 'smooth' });
    });
  });

  /* ---------- generic reveals ---------- */
  gsap.utils.toArray('.reveal').forEach((el) => {
    gsap.fromTo(el, { opacity: 0, y: 30 }, {
      opacity: 1, y: 0, duration: 0.9, ease: 'power3.out',
      scrollTrigger: { trigger: el, start: 'top 85%' }
    });
  });

  /* ---------- hero entrance ---------- */
  window.addEventListener('load', heroIn);
  function heroIn() {
    const words = gsap.utils.toArray('.hero-title .word');
    gsap.set('.fade-up', { opacity: 0, y: 24 });
    const tl = gsap.timeline({ delay: 0.2 });
    tl.from(words, { yPercent: 120, opacity: 0, duration: 1, ease: 'power4.out', stagger: 0.12 })
      .to('.fade-up', { opacity: 1, y: 0, duration: 0.8, ease: 'power2.out', stagger: 0.12 }, '-=0.5');
  }
  // also run once now in case 'load' already fired
  if (document.readyState === 'complete') heroIn();

  /* ---------- hero parallax (data-depth) ---------- */
  if (!reduce) {
    gsap.utils.toArray('#hero [data-depth]').forEach((layer) => {
      const depth = parseFloat(layer.dataset.depth) || 0.2;
      gsap.to(layer, {
        yPercent: depth * 60,
        ease: 'none',
        scrollTrigger: { trigger: '#hero', start: 'top top', end: 'bottom top', scrub: true }
      });
    });
  }

  /* ---------- typewriter story lines ---------- */
  const typeLines = gsap.utils.toArray('[data-type]');
  typeLines.forEach((el) => { el.dataset.full = el.textContent; el.textContent = ''; });
  ScrollTrigger.create({
    trigger: '#chapter-1',
    start: 'top 60%',
    once: true,
    onEnter: () => typeSequence(typeLines)
  });

  function typeSequence(lines) {
    let chain = Promise.resolve();
    lines.forEach((el) => {
      chain = chain.then(() => typeOne(el));
    });
  }
  function typeOne(el) {
    return new Promise((res) => {
      const full = el.dataset.full || '';
      if (reduce) { el.innerHTML = full; return res(); }
      let i = 0;
      el.textContent = '';
      const tick = () => {
        // preserve simple <b> tags by typing raw then swapping at end
        i++;
        el.textContent = full.replace(/<[^>]+>/g, '').slice(0, i);
        if (i < full.replace(/<[^>]+>/g, '').length) setTimeout(tick, 22);
        else { el.innerHTML = full; setTimeout(res, 220); }
      };
      tick();
    });
  }

  /* ---------- Oxytocin meter, linked to scroll progress ---------- */
  const lmFill = document.getElementById('lmFill');
  const lmPct = document.getElementById('lmPct');
  ScrollTrigger.create({
    trigger: document.body,
    start: 'top top',
    end: 'bottom bottom',
    onUpdate: (self) => {
      const v = Math.round(self.progress * 100);
      if (lmFill) lmFill.style.width = v + '%';
      if (lmPct) lmPct.textContent = v + '%';
    }
  });

  ScrollTrigger.refresh();

  /* ---------- fallbacks (no GSAP) ---------- */
  function setupOxytocinFallback() {
    const lmFill = document.getElementById('lmFill');
    const lmPct = document.getElementById('lmPct');
    const onScroll = () => {
      const h = document.documentElement;
      const p = Math.round((h.scrollTop / (h.scrollHeight - h.clientHeight)) * 100) || 0;
      if (lmFill) lmFill.style.width = p + '%';
      if (lmPct) lmPct.textContent = p + '%';
    };
    addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }
  function setupTypewriterFallback() {
    document.querySelectorAll('[data-type]').forEach(el => { /* leave text as-is */ });
  }
})();
