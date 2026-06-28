/* Service Worker для PWA — кэширование для офлайн-доступа */
const CACHE_NAME = 'lilsolid-v3';

self.addEventListener('install', (e) => {
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  if (e.request.method !== 'GET') return;
  const url = new URL(e.request.url);
  if (url.origin !== self.location.origin) return;
  /* HTML-страницы — всегда с сервера (без кэша), чтобы обновления применялись */
  const isNav = e.request.mode === 'navigate' || e.request.destination === 'document';
  const fetchOpts = isNav ? { cache: 'reload' } : {};
  e.respondWith(
    fetch(e.request, fetchOpts).then((res) => {
      const clone = res.clone();
      if (res.ok && !url.pathname.startsWith('/admin') && !isNav) {
        caches.open(CACHE_NAME).then((cache) => cache.put(e.request, clone));
      }
      return res;
    }).catch(() => caches.match(e.request))
  );
});
