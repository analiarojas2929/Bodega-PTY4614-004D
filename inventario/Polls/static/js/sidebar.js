document.addEventListener("DOMContentLoaded", () => {
    const sidebar = document.querySelector(".sidebar");
    const toggleButton = document.querySelector("#sidebarToggle");

    if (sidebar && toggleButton) {
        toggleButton.addEventListener("click", () => {
            sidebar.classList.toggle("collapsed");

            // Iterar sobre todos los elementos de los enlaces de la barra lateral
            const navLinks = document.querySelectorAll(".nav-link");
            navLinks.forEach(link => {
                const icon = link.querySelector("i");
                const text = link.querySelector("span");

                if (sidebar.classList.contains("collapsed")) {
                    // Ocultar el texto y centrar el ícono
                    if (text) text.style.display = "none";
                    if (icon) icon.style.marginRight = "0";
                } else {
                    // Mostrar el texto y restablecer el margen del ícono
                    if (text) text.style.display = "inline";
                    if (icon) icon.style.marginRight = "10px";
                }
            });
        });
    } else {
        console.error("El sidebar o el botón toggle no se encontraron.");
    }
});
