const reportsUrl = "/reports/";

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
            displayReport(data.reportData, formData.get('reportType'));
        } else {
            alert("Error al generar el reporte.");
        }
    } catch (error) {
        console.error("Error:", error);
        alert("Hubo un problema con la solicitud.");
    }
}

function displayReport(data, reportType) {
    const reportPreview = document.getElementById('reportPreview');
    reportPreview.innerHTML = '';

    if (data.length > 0) {
        let table = `<table class="table table-bordered">
            <thead>
                <tr>`;

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
