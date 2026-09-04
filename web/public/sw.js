/* 1440 Intelligence service worker (hand-rolled; App Router friendly).
 *
 *  - App shell + static assets (/_next/static, fonts, icons, logo): cache-first.
 *  - /api/* GET (JSON and the brief PDFs): network-first, falling back to the cache so
 *    briefs already opened remain readable offline. Only 2xx responses are stored;
 *    401s and errors never are. Non-GET requests are never intercepted.
 *  - Navigations: network-first; offline → the cached page for that URL, else the
 *    cached app shell ("/").
 */
const VERSION = "1440-intel-v1";
const SHELL_CACHE = `${VERSION}-shell`;
const STATIC_CACHE = `${VERSION}-static`;
const API_CACHE = `${VERSION}-api`;
const PDF_CACHE = `${VERSION}-pdf`;

const SHELL_URLS = [
  "/",
  "/manifest.webmanifest",
  "/icon-192.png",
  "/icon-512.png",
  "/apple-touch-icon.png",
  "/logo-gold.png",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches
      .open(SHELL_CACHE)
      .then((cache) => Promise.allSettled(SHELL_URLS.map((u) => cache.add(u))))
      .then(() => self.skipWaiting()),
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) =>
        Promise.all(keys.filter((k) => !k.startsWith(VERSION)).map((k) => caches.delete(k))),
      )
      .then(() => self.clients.claim()),
  );
});

self.addEventListener("message", (event) => {
  if (event.data === "clear-caches") {
    event.waitUntil(caches.keys().then((keys) => Promise.all(keys.map((k) => caches.delete(k)))));
  }
});

function isStatic(url) {
  return (
    url.pathname.startsWith("/_next/static/") ||
    url.pathname.startsWith("/_next/image") ||
    url.pathname.startsWith("/fonts/") ||
    /\.(png|ico|svg|webmanifest|woff2?|ttf)$/.test(url.pathname)
  );
}

async function cacheFirst(request, cacheName) {
  const cache = await caches.open(cacheName);
  const hit = await cache.match(request);
  if (hit) return hit;
  const res = await fetch(request);
  if (res.ok) cache.put(request, res.clone());
  return res;
}

async function networkFirst(request, cacheName, fallbackToShell) {
  const cache = await caches.open(cacheName);
  try {
    const res = await fetch(request);
    if (res.ok && res.status === 200) cache.put(request, res.clone());
    return res;
  } catch (err) {
    const hit = await cache.match(request);
    if (hit) return hit;
    if (fallbackToShell) {
      const shell = await caches.open(SHELL_CACHE);
      const home = await shell.match("/");
      if (home) return home;
    }
    throw err;
  }
}

self.addEventListener("fetch", (event) => {
  const { request } = event;
  if (request.method !== "GET") return;
  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;

  if (url.pathname.startsWith("/auth/")) return; // never cache auth

  if (request.mode === "navigate") {
    event.respondWith(networkFirst(request, SHELL_CACHE, true));
    return;
  }
  if (isStatic(url)) {
    event.respondWith(cacheFirst(request, STATIC_CACHE));
    return;
  }
  if (url.pathname.startsWith("/api/")) {
    const isPdf = /\/api\/briefs\/\d+\/pdf$/.test(url.pathname);
    event.respondWith(networkFirst(request, isPdf ? PDF_CACHE : API_CACHE, false));
  }
});
