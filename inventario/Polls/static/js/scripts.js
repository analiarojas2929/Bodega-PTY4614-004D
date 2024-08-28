document.addEventListener('DOMContentLoaded', function () {
    const notificationBell = document.querySelector('.notification_bell');
    const notificationDropdown = document.querySelector('.notification_dropdown');
    const closeNotification = document.querySelector('.close_notification');
  
    // Toggle the notification dropdown
    notificationBell.addEventListener('click', function () {
      notificationDropdown.style.display = notificationDropdown.style.display === 'block' ? 'none' : 'block';
    });
  
    // Close notification dropdown
    closeNotification.addEventListener('click', function () {
      notificationDropdown.style.display = 'none';
    });
  
    // Close dropdown if clicked outside
    window.addEventListener('click', function (e) {
      if (!notificationBell.contains(e.target) && !notificationDropdown.contains(e.target)) {
        notificationDropdown.style.display = 'none';
      }
    });
  });
  