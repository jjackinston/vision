/**
 * SellerVision AI — Service Worker
 *
 * Strategy:
 *   Static assets (_next/static, fonts, images)  → Cache-first
 *   Navigation (HTML documents)                  → Network-first with offline fallback
 *   API calls (/api/v1/*)                         → Network-only (never cache sensitive data)
 *   Everything else                               → Network-first
 *
 * Cache busting: increment CACHE_VERSION on each deploy.
 * The activate handler deletes all stale caches automatically.
 */

const CACHE_VERSION = "sv-v1";
const STATIC_CACHE  = `${CACHE_VERSION}-static`;
const PAGE_CACHE    = `${CACHE_VERSION}-pages`;

// Pages pre-cached on install (app shell)
const APP_SHELL = ["/", "/dashboard", "/products", "/analytics", "/offline"];

// Static asset patterns to cache on first fetch
const STATIC_PATTERNS = [
  /\/_next\/static\//,
  /\/fonts\//,
  /\.(?:woff2?|ttf|otf)$/,
];

// ── Install ────────────────────────────────────────────────────────────
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches
      .open(PAGE_CACHE)
      .then((cache) =>
        cache.addAll(APP_SHELL.filter((url) => url !== "/offline")).catch(() => {
          // Non-fatal: offline page may not exist yet
        })
      )
      .then(() => self.skipWaiting())
  );
});

// ── Activate ──────────────────────────────────────────────────────────
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((names) =>
        Promise.all(
          names
            .filter((n) => n !== STATIC_CACHE && n !== PAGE_CACHE)
            .map((n) => caches.delete(n))
        )
      )
      .then(() => self.clients.claim())
  );
});

// ── Fetch ─────────────────────────────────────────────────────────────
self.addEventListener("fetch", (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Only handle same-origin GET requests
  if (request.method !== "GET" || url.origin !== self.location.origin) return;

  // API calls: network-only — never cache auth'd responses
  if (url.pathname.startsWith("/api/")) return;

  // Static assets: cache-first
  if (STATIC_PATTERNS.some((p) => p.test(url.pathname))) {
    event.respondWith(cacheFirst(request, STATIC_CACHE));
    return;
  }

  // Navigation + everything else: network-first with offline fallback
  if (request.destination === "document") {
    event.respondWith(networkFirstDocument(request));
    return;
  }

  // Other same-origin resources: stale-while-revalidate
  event.respondWith(staleWhileRevalidate(request, STATIC_CACHE));
});

// ── Strategies ────────────────────────────────────────────────────────

async function cacheFirst(request, cacheName) {
  const cached = await caches.match(request);
  if (cached) return cached;
  const response = await fetch(request);
  if (response.ok) {
    const cache = await caches.open(cacheName);
    cache.put(request, response.clone());
  }
  return response;
}

async function networkFirstDocument(request) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(PAGE_CACHE);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    // Network failed — try cache, then offline fallback
    const cached = await caches.match(request);
    if (cached) return cached;
    const offline = await caches.match("/offline");
    if (offline) return offline;
    // Last resort: bare 503
    return new Response("<h1>Offline</h1><p>No internet connection.</p>", {
      status: 503,
      headers: { "Content-Type": "text/html" },
    });
  }
}

async function staleWhileRevalidate(request, cacheName) {
  const cache = await caches.open(cacheName);
  const cached = await cache.match(request);
  const fetchPromise = fetch(request).then((response) => {
    if (response.ok) cache.put(request, response.clone());
    return response;
  });
  return cached ?? fetchPromise;
}
