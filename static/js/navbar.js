// =========================================================
// AgriGuard Navigation System V3
// =========================================================

document.addEventListener("DOMContentLoaded", function () {

    const menuBtn = document.getElementById("menuBtn");
    const navLinks = document.getElementById("navLinks");
    const profileBtn = document.getElementById("profileBtn");

    if (!menuBtn || !navLinks) {
        return;
    }


    // =====================================================
    // MOBILE MENU
    // =====================================================

    function openMenu() {

        navLinks.classList.add("show");

        menuBtn.setAttribute("aria-expanded", "true");

        menuBtn.setAttribute(
            "aria-label",
            "Close navigation menu"
        );

        const icon = menuBtn.querySelector(".hamburger-icon");

        if (icon) {
            icon.textContent = "✕";
        }

    }


    function closeMenu() {

        navLinks.classList.remove("show");

        menuBtn.setAttribute("aria-expanded", "false");

        menuBtn.setAttribute(
            "aria-label",
            "Open navigation menu"
        );

        const icon = menuBtn.querySelector(".hamburger-icon");

        if (icon) {
            icon.textContent = "☰";
        }

    }


    function toggleMenu() {

        const isOpen =
            navLinks.classList.contains("show");

        if (isOpen) {

            closeMenu();

        } else {

            openMenu();

        }

    }


    menuBtn.addEventListener(
        "click",
        function (event) {

            event.stopPropagation();

            toggleMenu();

        }
    );


    // =====================================================
    // CLOSE MENU AFTER CLICKING A LINK
    // =====================================================

    const navAnchors =
        navLinks.querySelectorAll("a");

    navAnchors.forEach(function (link) {

        link.addEventListener(
            "click",
            function () {

                closeMenu();

            }
        );

    });


    // =====================================================
    // CLOSE MENU WHEN CLICKING OUTSIDE
    // =====================================================

    document.addEventListener(
        "click",
        function (event) {

            const clickedNavbar =
                event.target.closest(".navbar");

            if (!clickedNavbar) {

                closeMenu();

            }

        }
    );


    // =====================================================
    // PROFILE BUTTON
    // =====================================================

    if (profileBtn) {

        profileBtn.addEventListener(
            "click",
            function (event) {

                event.stopPropagation();

                const profileMenu =
                    profileBtn.closest(".profile-menu");

                if (!profileMenu) {
                    return;
                }

                const isOpen =
                    profileMenu.classList.toggle("open");

                profileBtn.setAttribute(
                    "aria-expanded",
                    isOpen
                );

            }
        );

    }


    // =====================================================
    // CLOSE PROFILE WHEN CLICKING OUTSIDE
    // =====================================================

    document.addEventListener(
        "click",
        function (event) {

            const profileMenu =
                document.querySelector(".profile-menu");

            if (!profileMenu) {
                return;
            }

            if (!event.target.closest(".profile-menu")) {

                profileMenu.classList.remove("open");

                if (profileBtn) {

                    profileBtn.setAttribute(
                        "aria-expanded",
                        "false"
                    );

                }

            }

        }
    );


    // =====================================================
    // DESKTOP / MOBILE RESIZE
    // =====================================================

    window.addEventListener(
        "resize",
        function () {

            if (window.innerWidth > 768) {

                closeMenu();

            }

        }
    );


    // =====================================================
    // ESCAPE KEY
    // =====================================================

    document.addEventListener(
        "keydown",
        function (event) {

            if (event.key === "Escape") {

                closeMenu();

                const profileMenu =
                    document.querySelector(".profile-menu");

                if (profileMenu) {

                    profileMenu.classList.remove("open");

                }

                if (profileBtn) {

                    profileBtn.setAttribute(
                        "aria-expanded",
                        "false"
                    );

                }

            }

        }
    );

});