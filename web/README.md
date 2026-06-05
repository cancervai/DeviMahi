# DeviMahi · "Goddess of Love & Peace" 🌸

A hand-built, hyper-animated **Studio-Ghibli-style romantic storytelling website** for Mahi.
Scroll-driven journey of bouquets, jokes, worship, memes, and one very serious shrine —
engineered to hit maximum oxytocin & serotonin. 💛

## What's inside
- **Pure static site** — no build step. Just open `index.html`.
- **Smooth scroll** (Lenis) + **scroll animations** (GSAP ScrollTrigger), loaded from CDN.
- **Custom canvas petal system** (`js/petals.js`) that reacts to the cursor.
- **Heart-trail cursor, konami code, and a hidden `love` typing trigger** (`js/easter-eggs.js`).
- **Interactive bouquet**, **Shrine of the Holy Feet** (comedy), **meme gallery**,
  a **catch-the-hearts mini-game**, a **WebAudio music-box toggle**, and a floating
  **compliment generator** (`js/main.js`).
- **Mobile-first & responsive**, with a `prefers-reduced-motion` fallback.

## The journey
Loader → Hero invocation → Ch.I How It Began → Ch.II Bouquet of Reasons →
Ch.III The Goddess Revealed → Ch.IV Shrine of the Holy Feet →
Ch.V Hall of Memes → Ch.VI Serotonin Station (mini-game) → Finale.

## Run locally
```bash
cd web
python3 -m http.server 8000
# open http://localhost:8000
```

## Deploy (same options as the game in ../DEPLOY.md)
It's a static folder, so any static host works:
- **GitHub Pages**: point Pages at this folder (or copy its contents to your Pages branch/dir).
- **Vercel / Netlify**: set the output/publish directory to `web/`.

## Assets
- `assets/photos/` — Mahi's real photos, given a soft painterly "Ghibli" CSS treatment.
- `assets/memes/` — the cat-and-fan meme and the shrine relic.
- AI-generated Ghibli scenes can be dropped into `assets/img/` later (the layout already
  leaves room); the current scenery is hand-built in SVG/CSS so it works fully offline.

## Easter eggs (don't tell Mahi)
- Type **`love`** anywhere → heart explosion + secret message.
- **Konami code** (↑↑↓↓←→←→ B A) → goddess buff + petal storm.
- Fill the Serotonin meter to **100%** → unlocks a hidden love note.
- The compliment button (bottom-left) never runs out. Neither do I.
