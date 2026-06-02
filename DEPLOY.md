# Deploying Nocturne of Paws to the web

The game is compiled to WebAssembly with **pygbag** and the static site lives
in [`site/`](site/) (`index.html` + `nocturne_of_paws.apk` + `favicon.png`).
The browser loads the Python/WASM runtime from the pygame-web CDN at
`https://pygame-web.github.io/cdn/0.9.3/` at play time, so the deployed site is
tiny and needs no build step on the host.

`vercel.json` is already configured for a **prebuilt static deploy**
(`outputDirectory: "site"`, no build/install command) with cross-origin
isolation headers.

## Option A — Vercel dashboard (no CLI, ~2 min)
1. Go to https://vercel.com/new and **Import** the `cancervai/devimahi` repo.
2. Framework Preset: **Other**. Leave Root Directory as the repo root
   (it will pick up `vercel.json` → serves `site/`).
3. **Project Name:** `mahiithenocturnalpaws` → your URL becomes
   `https://mahiithenocturnalpaws.vercel.app`.
4. Deploy.

## Option B — Vercel CLI locally (~1 min)
```bash
npm i -g vercel          # or use npx
cd /path/to/DeviMahi
vercel deploy --prod     # first run prompts a one-time login
# when asked for the project name, enter: mahiithenocturnalpaws
```

## Option C — Netlify (drag & drop)
Drag the `site/` folder onto https://app.netlify.com/drop, then rename the
site to `mahiithenocturnalpaws` in Site settings → Domain management to get
`https://mahiithenocturnalpaws.netlify.app`.

## Rebuilding the web bundle
```bash
cd nocturne_of_paws
python -m pygbag --build --template web_template.tmpl --icon favicon.png main.py
cp -f build/web/* ../site/
```

## Controls (web)
- Move: Arrow keys / WASD   • Run: Shift   • Jump: Space
- Rest / Cuddle / Anchor: hold **H** (or hold the mouse button)
- Advance dialogue: Enter
