document.addEventListener("DOMContentLoaded", () => {
    const body = document.querySelector("body");
    const darkLight = document.querySelector("#darkLight");
    const sidebar = document.querySelector(".sidebar");
    const submenuItems = document.querySelectorAll(".submenu_item");
    const sidebarOpen = document.querySelector("#sidebarOpen");
    const sidebarClose = document.querySelector(".collapse_sidebar");
    const sidebarExpand = document.querySelector(".expand_sidebar");
    const bellIcon = document.querySelector(".bx-bell");
    const modal = document.getElementById("notificationModal");
    const closeButton = document.querySelector(".close_button");

    // Manejar apertura y cierre del sidebar
    function handleSidebarToggle() {
        if (window.innerWidth < 768) {
            sidebar.classList.add("close");
            sidebarOpen.style.display = "block";
        } else {
            sidebar.classList.remove("close");
            sidebarOpen.style.display = "none";
        }
    }

    window.addEventListener("resize", handleSidebarToggle);
    handleSidebarToggle(); // Initial check

    sidebarOpen.addEventListener("click", () => {
        sidebar.classList.toggle("close");
    });

    sidebarClose.addEventListener("click", () => {
        sidebar.classList.add("close", "hoverable");
    });

    sidebarExpand.addEventListener("click", () => {
        sidebar.classList.remove("close", "hoverable");
    });

    sidebar.addEventListener("mouseenter", () => {
        if (sidebar.classList.contains("hoverable")) {
            sidebar.classList.remove("close");
        }
    });

    sidebar.addEventListener("mouseleave", () => {
        if (sidebar.classList.contains("hoverable")) {
            sidebar.classList.add("close");
        }
    });

    darkLight.addEventListener("click", () => {
        body.classList.toggle("dark");
        if (body.classList.contains("dark")) {
            darkLight.classList.replace("bx-sun", "bx-moon");
        } else {
            darkLight.classList.replace("bx-moon", "bx-sun");
        }
    });

    submenuItems.forEach((item, index) => {
        item.addEventListener("click", () => {
            item.classList.toggle("show_submenu");
            submenuItems.forEach((item2, index2) => {
                if (index !== index2) {
                    item2.classList.remove("show_submenu");
                }
            });
        });
    });

    // Abrir y cerrar ventana de notificaciones
    bellIcon.addEventListener("click", (event) => {
        event.stopPropagation();
        notificationTab.classList.toggle("open");
    });

    // Cerrar ventana de notificaciones al hacer clic fuera de ella
    document.addEventListener("click", (event) => {
        if (!notificationTab.contains(event.target)) {
            notificationTab.classList.remove("open");
        }
    });

    // Manejar clic en notificaciones
    bellIcon.addEventListener("click", () => {
        modal.style.display = "block";
    });

    // Cerrar modal cuando se hace clic en la "X"
    closeButton.addEventListener("click", () => {
        modal.style.display = "none";
    });

    // Cerrar modal cuando se hace clic fuera del contenido del modal
    window.addEventListener("click", (event) => {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    });

    // Manejar clic en notificaciones dentro del modal
    const notifications = document.querySelectorAll(".modal_notifications .notification");
    notifications.forEach((notification) => {
        notification.addEventListener("click", () => {
            console.log("Notification clicked:", notification.textContent);
            notification.remove(); // Eliminar notificación clicada
        });
    });
});
