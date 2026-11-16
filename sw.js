// Offline support for the Bible Reader.
//
// - The app page itself: try the network first (so updates arrive), fall back to the saved copy.
// - Everything else on this site (Bible versions, commentaries, classic writings under data/):
//   serve the saved copy immediately when there is one, otherwise download and keep it.
//   Saved copies older than a day are quietly refreshed in the background.
//
// Nothing is downloaded ahead of time: the full library is hundreds of megabytes, so only
// what the reader actually opens is stored on the device.

const CACHE = 'bible-library-v1'; // keep in sync with DATA_CACHE in index.html
const REFRESH_AFTER_MS = 24 * 60 * 60 * 1000;
const PAGE_TIMEOUT_MS = 4000;

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE)
      .then((cache) => cache.add(new Request('./', { cache: 'reload' })))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil((async () => {
    const names = await caches.keys();
    await Promise.all(names.filter((name) => name.startsWith('bible-library-') && name !== CACHE).map((name) => caches.delete(name)));
    await self.clients.claim();
  })());
});

function isStorable(response) {
  return response && response.ok && response.type === 'basic';
}

async function pageResponse(request) {
  const cache = await caches.open(CACHE);
  const saved = (await cache.match(request, { ignoreSearch: true })) || (await cache.match('./'));
  const fresh = fetch(request).then((response) => {
    if (isStorable(response)) {
      cache.put('./', response.clone());
    }
    return response;
  });
  if (!saved) {
    return fresh;
  }
  // Slow or missing connection: do not leave the reader staring at a blank screen.
  const timeout = new Promise((resolve) => setTimeout(() => resolve(null), PAGE_TIMEOUT_MS));
  const winner = await Promise.race([fresh.catch(() => null), timeout]);
  return winner && winner.ok ? winner : saved;
}

async function assetResponse(event) {
  const request = event.request;
  const cache = await caches.open(CACHE);
  const saved = await cache.match(request);
  if (!saved) {
    const response = await fetch(request);
    if (isStorable(response)) {
      event.waitUntil(cache.put(request, response.clone()));
    }
    return response;
  }
  const savedAt = Date.parse(saved.headers.get('date') || '');
  if (!savedAt || Date.now() - savedAt > REFRESH_AFTER_MS) {
    event.waitUntil(
      fetch(request)
        .then((response) => (isStorable(response) ? cache.put(request, response) : undefined))
        .catch(() => undefined)
    );
  }
  return saved;
}

self.addEventListener('fetch', (event) => {
  const request = event.request;
  if (request.method !== 'GET' || request.headers.has('range')) {
    return;
  }
  const url = new URL(request.url);
  if (url.origin !== self.location.origin || url.pathname.endsWith('/sw.js')) {
    return;
  }
  if (request.mode === 'navigate') {
    event.respondWith(pageResponse(request));
    return;
  }
  event.respondWith(assetResponse(event));
});
