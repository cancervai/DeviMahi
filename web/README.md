# For Mahi · after dark 🖤

A hand-built, hyper-animated **love letter for Mahi** — written in the dark, in poetry,
with very little dignity. A moody, candlelit, scroll-driven journey: bouquets, worship,
nonchalant jokes, and one very serious shrine.

## What's inside
- **Pure static site** — no build step. Just open `index.html`.
- **Smooth scroll** (Lenis, desktop only) + **scroll animations** (GSAP ScrollTrigger), from CDN.
- **Custom canvas petal system** that reacts to cursor / touch.
- **Heart-trail cursor (desktop), konami code, hidden `love` trigger** (`js/easter-eggs.js`).
- **Interactive bouquet** of things he doesn't say out loud, the **Shrine of the Holy Feet**,
  a **catch-what-i-throw-you** mini-game, a **music-box toggle**, and a floating
  **"here's what i'm thinking rn"** button (`js/main.js`).

## The journey
Loader → Hero → **i.** how the night began → **ii.** a bouquet of things i don't say out loud →
**iii.** the goddess, unveiled → **iv.** the shrine of the holy feet → **v.** catch what i throw you →
finale.

## Built for iPhone 6 Plus / iOS Safari 12
Mobile-first and tuned for an older A8 device. No CSS feature that Safari 12 lacks
(`inset`, flex `gap`, `aspect-ratio`, `clamp()`, `100svh`, unprefixed `backdrop-filter`)
is used without a fallback; no Pointer Events or WAAPI in the JS; smooth-scroll, parallax
and the heart-trail are disabled on touch devices; particle counts are trimmed. The design
is unchanged — it just runs everywhere. A `prefers-reduced-motion` fallback is included.

## Run locally
```bash
cd web
python3 -m http.server 8000   # open http://localhost:8000
```

## Deploy
Static folder — any static host works. In this repo it's published via GitHub Pages
(served from `/docs`), with the small WASM game living at `/game/`.

## Easter eggs (don't tell Mahi)
- Type **`love`** anywhere → a quiet explosion + a line meant only for her.
- **Konami code** (↑↑↓↓←→←→ B A) → kiss the moon.
- Fill the meter to **100%** in the little game → a hidden line unlocks.
- The button bottom-left never runs out of thoughts. Neither does he.
