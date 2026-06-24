const CACHE = "calorie-tracker-v1";
const PRECACHE_URLS = ["/", "/static/css/style.css", "/static/manifest.json"];

self.addEventListener("install", (e) => {
    e.waitUntil(
        caches.open(CACHE).then((cache) => cache.addAll(PRECACHE_URLS))
    );
});

self.addEventListener("fetch", (e) => {
    e.respondWith(
        caches.match(e.request).then((hit) => hit || fetch(e.request))
    );
});
