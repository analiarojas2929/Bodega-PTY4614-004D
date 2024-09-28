document.addEventListener("DOMContentLoaded", () => {
    const sidebar = document.querySelector(".sidebar");
    const toggleButton = document.querySelector("#sidebarToggle");
    const logoImage = sidebar.querySelector("img"); // Seleccionamos la imagen del logo

    if (sidebar && toggleButton && logoImage) {
        toggleButton.addEventListener("click", () => {
            sidebar.classList.toggle("collapsed");

            // Cambiar el icono del botón toggle según el estado del sidebar
            const toggleIcon = toggleButton.querySelector("i");
            if (sidebar.classList.contains("collapsed")) {
                toggleIcon.classList.remove("fa-bars");
                toggleIcon.classList.add("fa-times"); // Cambia el icono a "X"
            } else {
                toggleIcon.classList.remove("fa-times");
                toggleIcon.classList.add("fa-bars"); // Cambia el icono de nuevo a "hamburguesa"
            }

            // Iterar sobre todos los elementos de los enlaces de la barra lateral
            const navLinks = document.querySelectorAll(".nav-link");
            navLinks.forEach(link => {
                const icon = link.querySelector("i");
                const text = link.querySelector("span");

                if (sidebar.classList.contains("collapsed")) {
                    // Ocultar el texto y centrar el ícono
                    if (text) text.style.display = "none";
                    if (icon) icon.style.marginRight = "0";
                    logoImage.style.width = "50px"; // Cambiar tamaño del logo
                } else {
                    // Mostrar el texto y restablecer el margen del ícono
                    if (text) text.style.display = "inline";
                    if (icon) icon.style.marginRight = "10px";
                    logoImage.style.width = "120px"; // Restaurar tamaño del logo
                }
            });
        });
    } else {
        console.error("El sidebar, el botón toggle o la imagen del logo no se encontraron.");
    }
});
