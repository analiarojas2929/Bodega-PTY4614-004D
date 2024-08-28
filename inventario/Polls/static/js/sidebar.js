document.addEventListener("DOMContentLoaded", () => {
    const body = document.querySelector("body");
    const darkLight = document.querySelector("#darkLight");
    const sidebar = document.querySelector(".sidebar");
    const sidebarOpen = document.querySelector("#sidebarOpen");
    const sidebarClose = document.querySelector(".collapse_sidebar");
    const sidebarExpand = document.querySelector(".expand_sidebar");

    // Manejar apertura y cierre del sidebar
    function handleSidebarToggle() {
        if (window.innerWidth < 768) {
            sidebar.classList.add("close");
            sidebar.classList.remove("open");
            sidebarOpen.style.display = "block"; // Muestra el botón hamburguesa
        } else {
            sidebar.classList.remove("close");
            sidebar.classList.remove("open");
            sidebarOpen.style.display = "none"; // Oculta el botón hamburguesa
        }
    }

    window.addEventListener("resize", handleSidebarToggle);
    handleSidebarToggle(); // Inicializa el estado correcto

    sidebarOpen.addEventListener("click", () => {
        sidebar.classList.toggle("open");
        sidebar.classList.toggle("close");
    });

    sidebarClose.addEventListener("click", () => {
        sidebar.classList.add("close");
        sidebar.classList.remove("open");
    });

    sidebarExpand.addEventListener("click", () => {
        sidebar.classList.remove("close");
        sidebar.classList.add("open");
    });

    darkLight.addEventListener("click", () => {
        body.classList.toggle("dark");
        if (body.classList.contains("dark")) {
            darkLight.classList.replace("bx-sun", "bx-moon");
        } else {
            darkLight.classList.replace("bx-moon", "bx-sun");
        }
    });

    // Manejo del submenú
    const submenuItems = document.querySelectorAll(".submenu_item");
    submenuItems.forEach((item) => {
        item.addEventListener("click", () => {
            item.classList.toggle("show_submenu");
            submenuItems.forEach((item2) => {
                if (item !== item2) {
                    item2.classList.remove("show_submenu");
                }
            });
        });
    });
});
