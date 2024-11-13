const reportsUrl = "/reports/";
let myChart = null;

// Asegurarnos de que el DOM esté cargado antes de ejecutar el código
document.addEventListener('DOMContentLoaded', function () {
    // Inicializar Flatpickr para los campos de fecha
    flatpickr("#startDate", {
        dateFormat: "d-m-Y",
        altInput: true,
        altFormat: "d-m-Y",
        allowInput: true,
        locale: "es"
    });
    flatpickr("#endDate", {
        dateFormat: "d-m-Y",
        altInput: true,
        altFormat: "d-m-Y",
        allowInput: true,
        locale: "es"
    });

    // Asignar eventos a los botones de exportación
    const exportToPDF = document.getElementById('exportToPDF');
    if (exportToPDF) {
        exportToPDF.addEventListener('click', exportPDF);
    }

    const exportToExcel = document.getElementById('exportToExcel');
    if (exportToExcel) {
        exportToExcel.addEventListener('click', exportExcel);
    }

    // Asignar evento al formulario
    const reportForm = document.getElementById('reportForm');
    if (reportForm) {
        reportForm.addEventListener('submit', generateReport);
    }
});

// Función para generar el reporte al enviar el formulario
async function generateReport(event) {
    event.preventDefault();
    const formData = new FormData(document.getElementById('reportForm'));

    try {
        const response = await fetch(reportsUrl, {
            method: 'POST',
            headers: {
                'X-CSRFToken': formData.get('csrfmiddlewaretoken')
            },
            body: formData
        });

        if (response.ok) {
            const data = await response.json();
            const reportType = formData.get('reportType');

            // Mostrar el reporte en la tabla
            displayReport(data.reportData, reportType);

            // Generar el gráfico si hay datos
            if (data.reportData.length > 0) {
                renderChart(data.reportData, reportType);
            } else {
                clearChart();
            }
        } else {
            alert("Error al generar el reporte.");
        }
    } catch (error) {
        console.error("Error:", error);
        alert("Hubo un problema con la solicitud.");
    }
}

// Función para mostrar los datos en una tabla
function displayReport(data, reportType) {
    const reportPreview = document.getElementById('reportPreview');
    reportPreview.innerHTML = '';

    if (data.length > 0) {
        let table = `<table class="table table-striped table-hover">
            <thead>
                <tr>`;

        // Encabezados según el tipo de reporte
        if (reportType === 'Inventario Actual') {
            table += `<th>ID</th><th>Nombre</th><th>Descripción</th><th>Unidad Medida</th><th>Cantidad Disponible</th><th>Stock Mínimo</th><th>Estado</th>`;
        } else if (reportType === 'Alertas de Stock bajo') {
            table += `<th>Material</th><th>Cantidad Disponible</th><th>Stock Mínimo</th><th>Unidad de Medida</th><th>Alerta</th>`;
        } else if (reportType === 'Movimientos de stock') {
            table += `<th>Material</th><th>Cantidad</th><th>Estado</th><th>Fecha de Creación</th>`;
        }

        table += `</tr></thead><tbody>`;

        data.forEach((row) => {
            table += '<tr>';
            if (reportType === 'Inventario Actual') {
                table += `<td>${row.id}</td><td>${row.nombre}</td><td>${row.descripcion}</td><td>${row.unidad_medida__descripcion}</td><td>${row.cantidad_disponible}</td><td>${row.stock}</td><td>${row.activo ? 'Activo' : 'Inactivo'}</td>`;
            } else if (reportType === 'Alertas de Stock bajo') {
                const alerta = row.alerta_stock ? '<span class="text-danger">Stock Bajo</span>' : 'Ok';
                table += `<td>${row.material}</td><td>${row.cantidad_disponible}</td><td>${row.stock}</td><td>${row.unidad_medida}</td><td>${alerta}</td>`;
            } else if (reportType === 'Movimientos de stock') {
                table += `<td>${row.material}</td><td>${row.cantidad}</td><td>${row.estado}</td><td>${row.fecha_creacion}</td>`;
            }
            table += '</tr>';
        });

        table += '</tbody></table>';
        reportPreview.innerHTML = table;
    } else {
        reportPreview.innerHTML = '<p class="text-muted">No se encontraron datos</p>';
    }
}

// Función para generar el gráfico utilizando Chart.js
function renderChart(data, reportType) {
    const ctx = document.getElementById('reportChart').getContext('2d');
    let labels = [];
    let values = [];

    if (reportType === 'Inventario Actual') {
        labels = data.map(item => item.nombre);
        values = data.map(item => item.cantidad_disponible);
    } else if (reportType === 'Alertas de Stock bajo') {
        labels = data.map(item => item.material);
        values = data.map(item => item.cantidad_disponible);
    } else if (reportType === 'Movimientos de stock') {
        labels = data.map(item => item.material);
        values = data.map(item => item.cantidad);
    }

    clearChart();

    myChart = new Chart(ctx, {
        type: reportType === 'Movimientos de stock' ? 'line' : 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Cantidad',
                data: values,
                backgroundColor: 'rgba(54, 162, 235, 0.6)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Función para limpiar el gráfico anterior
function clearChart() {
    if (myChart) {
        myChart.destroy();
        myChart = null;
    }
}

// Función para exportar a PDF
function exportPDF(event) {
    event.preventDefault();
    const reportType = document.getElementById('reportType').value;
    window.location.href = `/export_to_pdf/?reportType=${reportType}`;
}

// Función para exportar a Excel
function exportExcel(event) {
    event.preventDefault();
    const reportType = document.getElementById('reportType').value;
    window.location.href = `/export_to_excel/?reportType=${reportType}`;
}
