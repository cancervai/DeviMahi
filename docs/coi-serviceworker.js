/*
 * COI + Cache service worker
 *
 * 1. Injects COOP/COEP headers on every response so SharedArrayBuffer works
 *    on GitHub Pages (pygbag WASM requires it).
 * 2. Caches the pygame-web CDN files (~40 MB on first load) so every visit
 *    after the first loads instantly from disk — no network round-trip.
 */

const CACHE   = "nop-v2";                              // bump to invalidate
const CDN     = "https://pygame-web.github.io/cdn/";  // cache all CDN assets

// ── Lifecycle ──────────────────────────────────────────────────────────────
self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", e =>
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  )
);

// ── Helpers ────────────────────────────────────────────────────────────────
function addCOI(response) {
  const h = new Headers(response.headers);
  h.set("Cross-Origin-Opener-Policy",   "same-origin");
  h.set("Cross-Origin-Embedder-Policy", "credentialless");
  return new Response(response.body, {
    status: response.status, statusText: response.statusText, headers: h,
  });
}

function isCacheable(url) {
  return url.startsWith(CDN) ||
    (url.startsWith(self.location.origin) && !url.includes("index.html"));
}

// ── Fetch handler ──────────────────────────────────────────────────────────
async function handle(request) {
  if (request.cache === "only-if-cached" && request.mode !== "same-origin") return;

  // Serve from cache (instant on second+ loads)
  if (isCacheable(request.url)) {
    const hit = await caches.match(request);
    if (hit) return addCOI(hit);
  }

  // Network fetch
  let res;
  try { res = await fetch(request); } catch { return Response.error(); }
  if (!res || res.status === 0) return res;

  // Cache a clone for next time (fire-and-forget — don't block the response)
  if (isCacheable(request.url) && res.ok) {
    const clone = res.clone();
    caches.open(CACHE).then(c => c.put(request, clone));
  }

  return addCOI(res);
}

self.addEventListener("fetch", e => e.respondWith(handle(e.request)));
