/* Cross-Origin Isolation service worker
 * Injects COOP/COEP headers so SharedArrayBuffer is available on GitHub Pages.
 * Without these headers pygbag/WASM hangs with a blank screen.
 */
self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", e => e.waitUntil(self.clients.claim()));

async function handleFetch(request) {
  if (request.cache === "only-if-cached" && request.mode !== "same-origin") return;
  let response;
  try {
    response = await fetch(request);
  } catch {
    return Response.error();
  }
  if (!response || response.status === 0) return response;
  const headers = new Headers(response.headers);
  headers.set("Cross-Origin-Opener-Policy", "same-origin");
  headers.set("Cross-Origin-Embedder-Policy", "credentialless");
  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers,
  });
}

self.addEventListener("fetch", e => e.respondWith(handleFetch(e.request)));
