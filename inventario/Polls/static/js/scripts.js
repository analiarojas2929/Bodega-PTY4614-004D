document.addEventListener('DOMContentLoaded', function () {
  // Manejo de notificaciones
  const notificationBell = document.querySelector('.notification_bell');
  const notificationDropdown = document.querySelector('.notification_dropdown');
  const closeNotification = document.querySelector('.close_notification');
  const reportForm = document.getElementById('reportForm');
  const reportContent = document.getElementById('reportContent');

  // Inicialización de Chart.js
  const ctx = document.getElementById('inventoryChart');
  if (ctx) {
    const inventoryChart = new Chart(ctx.getContext('2d'), {
      type: 'bar',
      data: {
        labels: ['Cemento', 'Arena', 'Grava'],
        datasets: [{
          label: '# de Unidades',
          data: [50, 20, 30],
          backgroundColor: [
            'rgba(54, 162, 235, 0.2)',
            'rgba(255, 206, 86, 0.2)',
            'rgba(75, 192, 192, 0.2)'
          ],
          borderColor: [
            'rgba(54, 162, 235, 1)',
            'rgba(255, 206, 86, 1)',
            'rgba(75, 192, 192, 1)'
          ],
          borderWidth: 1
        }]
      },
      options: {
        scales: {
          y: {
            beginAtZero: true
          }
        }
      }
    });
  } else {
    console.error("Elemento canvas con ID 'inventoryChart' no encontrado.");
  }

  // Toggle del dropdown de notificaciones
  if (notificationBell && notificationDropdown && closeNotification) {
    notificationBell.addEventListener('click', function () {
      notificationDropdown.style.display = notificationDropdown.style.display === 'block' ? 'none' : 'block';
    });

    closeNotification.addEventListener('click', function () {
      notificationDropdown.style.display = 'none';
    });

    window.addEventListener('click', function (e) {
      if (!notificationBell.contains(e.target) && !notificationDropdown.contains(e.target)) {
        notificationDropdown.style.display = 'none';
      }
    });
  } else {
    console.error("Los elementos de notificaciones no se encuentran en el DOM.");
  }

  // Manejo del formulario de reportes
  if (reportForm && reportContent) {
    reportForm.addEventListener('submit', function (e) {
      e.preventDefault();
      const reportType = document.getElementById('reportType').value;
      const startDate = document.getElementById('startDate').value;
      const endDate = document.getElementById('endDate').value;
      reportContent.innerHTML = `<h3>Reporte: ${reportType}</h3><p>Del ${startDate} al ${endDate}</p>`;
    });
  } else {
    console.error("Formulario de reportes o contenido de reporte no encontrado.");
  }

  // Funcionalidad para exportar reportes
  const exportPdfButton = document.querySelector('.btn-success');
  const exportExcelButton = document.querySelector('.btn-info');

  if (exportPdfButton && exportExcelButton) {
    exportPdfButton.addEventListener('click', function () {
      console.log("Exportar a PDF clickeado");
      toastr.success('Reporte exportado a PDF.');
    });

    exportExcelButton.addEventListener('click', function () {
      console.log("Exportar a Excel clickeado");
      toastr.info('Reporte exportado a Excel.');
    });
  } else {
    console.error("Botones de exportación no encontrados.");
  }

  // Inicialización de DataTables
  if ($('table').length > 0) {
    $('table').DataTable({
      "paging": true,
      "searching": true,
      "ordering": true
    });
  } else {
    console.error("Tabla no encontrada para inicializar DataTables.");
  }
});

$(document).ready(function() {
  $('#ticketTable').DataTable({
      "paging": true,
      "searching": true,
      "ordering": true
  });
});