const reportsUrl = "/reports/";
let myChart = null; // Inicializar la variable global para el gráfico

// Función para generar el reporte al enviar el formulario
async function generateReport(event) {
    event.preventDefault();
    const formData = new FormData(document.getElementById('reportForm'));

    try {
        const response = await fetch(reportsUrl, {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const data = await response.json();
            const reportType = formData.get('reportType');
            
            // Mostrar el reporte en tabla
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
        let table = `<table class="table table-bordered">
            <thead>
                <tr>`;

        // Encabezados según el tipo de reporte
        if (reportType === 'Inventario Actual') {
            table += `
                <th>ID</th>
                <th>Nombre</th>
                <th>Descripción</th>
                <th>Unidad Medida</th>
                <th>Cantidad Disponible</th>
                <th>Stock Mínimo</th>
                <th>Estado</th>`;
        } else if (reportType === 'Alertas de Stock bajo') {
            table += `
                <th>Material</th>
                <th>Cantidad Disponible</th>
                <th>Stock Mínimo</th>
                <th>Unidad de Medida</th>
                <th>Alerta</th>`;
        } else if (reportType === 'Movimientos de stock') {
            table += `
                <th>Material</th>
                <th>Cantidad</th>
                <th>Estado</th>
                <th>Fecha de Creación</th>`;
        }

        table += `</tr></thead><tbody>`;

        data.forEach(row => {
            table += '<tr>';
            if (reportType === 'Inventario Actual') {
                table += `
                    <td>${row.id}</td>
                    <td>${row.nombre}</td>
                    <td>${row.descripcion}</td>
                    <td>${row.unidad_medida__descripcion}</td>
                    <td>${row.cantidad_disponible}</td>
                    <td>${row.stock}</td>
                    <td>${row.activo ? 'Activo' : 'Inactivo'}</td>`;
            } else if (reportType === 'Alertas de Stock bajo') {
                const alerta = row.alerta_stock ? '<span class="text-danger">Stock Bajo</span>' : 'Ok';
                table += `
                    <td>${row.material}</td>
                    <td>${row.cantidad_disponible}</td>
                    <td>${row.stock}</td>
                    <td>${row.unidad_medida}</td>
                    <td>${alerta}</td>`;
            } else if (reportType === 'Movimientos de stock') {
                table += `
                    <td>${row.material}</td>
                    <td>${row.cantidad}</td>
                    <td>${row.estado}</td>
                    <td>${row.fecha_creacion}</td>`;
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

function clearChart() {
    if (myChart) {
        myChart.destroy();
    }
}

function renderChart(data, reportType) {
    const ctx = document.getElementById('reportChart').getContext('2d');
    let labels = [];
    let values = [];
    let backgroundColor, borderColor;

    if (reportType === 'Inventario Actual') {
        labels = data.map(item => item.nombre);
        values = data.map(item => item.cantidad_disponible);
        backgroundColor = 'rgba(75, 192, 192, 0.6)';
        borderColor = 'rgba(75, 192, 192, 1)';
    } else if (reportType === 'Alertas de Stock bajo') {
        labels = data.map(item => item.material);
        values = data.map(item => item.cantidad_disponible);
        backgroundColor = 'rgba(255, 99, 132, 0.6)';
        borderColor = 'rgba(255, 99, 132, 1)';
    } else if (reportType === 'Movimientos de stock') {
        labels = data.map(item => item.material);
        values = data.map(item => item.cantidad);
        backgroundColor = 'rgba(54, 162, 235, 0.6)';
        borderColor = 'rgba(54, 162, 235, 1)';
    }

    clearChart();

    // Crear gradiente de color
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, backgroundColor);
    gradient.addColorStop(1, 'rgba(255, 255, 255, 0.1)');

    myChart = new Chart(ctx, {
        type: reportType === 'Movimientos de stock' ? 'line' : 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: reportType,
                data: values,
                backgroundColor: reportType === 'Movimientos de stock' ? gradient : backgroundColor,
                borderColor: borderColor,
                borderWidth: 2,
                tension: 0.3, // Suaviza la línea en el gráfico de tipo 'line'
                pointBackgroundColor: borderColor,
                fill: true
            }]
        },
        options: {
            responsive: true,
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Cantidad: ${context.raw}`;
                        }
                    }
                },
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        color: '#333',
                        font: {
                            size: 14
                        }
                    }
                }
            },
            scales: {
                x: {
                    ticks: {
                        color: '#555',
                        font: {
                            size: 12
                        }
                    }
                },
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: '#555',
                        font: {
                            size: 12
                        }
                    }
                }
            },
            animation: {
                duration: 1500,
                easing: 'easeOutBounce'
            }
        }
    });
}

// Función para exportar a PDF
document.getElementById('exportToPDF').addEventListener('click', function (event) {
    event.preventDefault();
    
    // Obtener los valores seleccionados en el formulario
    const reportType = document.getElementById('reportType').value;
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;

    // Verificar que el tipo de reporte esté seleccionado
    if (!reportType) {
        alert("Por favor, selecciona un tipo de reporte.");
        return;
    }

    // Construir la URL para la exportación a PDF con los parámetros seleccionados
    let url = `/export_to_pdf/?reportType=${encodeURIComponent(reportType)}`;
    
    if (startDate) {
        url += `&startDate=${encodeURIComponent(startDate)}`;
    }
    if (endDate) {
        url += `&endDate=${encodeURIComponent(endDate)}`;
    }

    // Redirigir al usuario para descargar el PDF
    window.location.href = url;
});

// Función para exportar a Excel
document.getElementById('exportToExcel').addEventListener('click', function (event) {
    event.preventDefault();
    
    const reportType = document.getElementById('reportType').value;
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;

    if (!reportType) {
        alert("Por favor, selecciona un tipo de reporte.");
        return;
    }

    let url = `/export_to_excel/?reportType=${encodeURIComponent(reportType)}`;
    if (startDate) url += `&startDate=${encodeURIComponent(startDate)}`;
    if (endDate) url += `&endDate=${encodeURIComponent(endDate)}`;

    window.location.href = url;
});
