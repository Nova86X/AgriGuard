const CACHE_NAME = "agriguard-v1";

const STATIC_FILES = [
    "/",
    "/static/manifest.json",
    "/static/css/navbar.css",
    "/static/images/agriguard_logo.png"
];


// =====================================================
// INSTALL
// =====================================================

self.addEventListener("install", event => {

    console.log("AgriGuard Service Worker installing...");

    event.waitUntil(

        caches.open(CACHE_NAME)
            .then(cache => {

                return cache.addAll(STATIC_FILES);

            })

    );

    self.skipWaiting();

});


// =====================================================
// ACTIVATE
// =====================================================

self.addEventListener("activate", event => {

    console.log("AgriGuard Service Worker activated.");

    event.waitUntil(

        caches.keys()
            .then(cacheNames => {

                return Promise.all(

                    cacheNames
                        .filter(name => name !== CACHE_NAME)
                        .map(name => caches.delete(name))

                );

            })

    );

    self.clients.claim();

});


// =====================================================
// FETCH
// =====================================================

self.addEventListener("fetch", event => {

    // Only handle GET requests
    if (event.request.method !== "GET") {
        return;
    }

    event.respondWith(

        fetch(event.request)

            .then(response => {

                // Save successful responses
                const responseClone = response.clone();

                caches.open(CACHE_NAME)
                    .then(cache => {

                        cache.put(
                            event.request,
                            responseClone
                        );

                    });

                return response;

            })

            .catch(() => {

                // If internet is unavailable,
                // try the cached version.

                return caches.match(
                    event.request
                );

            })

    );

});