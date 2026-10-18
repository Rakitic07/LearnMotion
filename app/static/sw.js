const CACHE_NAME = "learnmotion-shell-v1";
const APP_SHELL = [
  "/",
  "/static/manifest.webmanifest",
  "/static/img/pwa-192.png",
  "/static/img/pwa-512.png",
  "/static/img/pwa-maskable-512.png",
  "/static/img/apple-touch-icon.png",
  "/static/img/learnmotion-share.png",
];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(APP_SHELL)));
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) => Promise.all(keys.filter((key) => key.startsWith("learnmotion-shell-") && key !== CACHE_NAME).map((key) => caches.delete(key))))
      .then(() => self.clients.claim()),
  );
});

self.addEventListener("fetch", (event) => {
  const request = event.request;
  const url = new URL(request.url);
  if (request.method !== "GET" || url.origin !== self.location.origin || url.pathname.startsWith("/api/")) return;

  if (request.mode === "navigate") {
    event.respondWith((async () => {
      try {
        const response = await fetch(request);
        if (response.ok) await (await caches.open(CACHE_NAME)).put("/", response.clone());
        return response;
      } catch {
        return (await caches.match(request)) || (await caches.match("/"));
      }
    })());
    return;
  }

  if (url.pathname.startsWith("/static/")) {
    event.respondWith((async () => {
      try {
        const response = await fetch(request);
        if (response.ok) await (await caches.open(CACHE_NAME)).put(request, response.clone());
        return response;
      } catch {
        return (await caches.match(request)) || Response.error();
      }
    })());
  }
});
