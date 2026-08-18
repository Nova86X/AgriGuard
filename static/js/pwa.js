// =====================================================
// AGRIGUARD PWA SERVICE WORKER REGISTRATION
// =====================================================

if ("serviceWorker" in navigator) {

    window.addEventListener("load", () => {

        navigator.serviceWorker
            .register("/service-worker.js")

            .then(registration => {

                console.log(
                    "AgriGuard Service Worker registered:",
                    registration.scope
                );

            })

            .catch(error => {

                console.error(
                    "AgriGuard Service Worker registration failed:",
                    error
                );

            });

    });

}