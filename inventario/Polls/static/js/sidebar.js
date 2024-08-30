document.addEventListener("DOMContentLoaded", () => {
    const sidebarToggle = document.getElementById("sidebarToggle");
    const sidebarDropdown = document.getElementById("sidebarDropdown");
    const body = document.querySelector("body");
    const darkLight = document.querySelector("#darkLight");


    // Verifica si los elementos existen en el DOM
    if (sidebarToggle && sidebarDropdown) {
        sidebarToggle.addEventListener("click", () => {
            // Alterna la visibilidad del menú desplegable
            if (sidebarDropdown.style.display === "block") {
                sidebarDropdown.style.display = "none";
            } else {
                sidebarDropdown.style.display = "block";
            }
        });
    } else {
        console.error("sidebarToggle o sidebarDropdown no se encuentran en el DOM.");
    }
    darkLight.addEventListener("click", () => {
        body.classList.toggle("dark");
        if (body.classList.contains("dark")) {
            darkLight.classList.replace("bx-sun", "bx-moon");
        } else {
            darkLight.classList.replace("bx-moon", "bx-sun");
        }
    });
});
