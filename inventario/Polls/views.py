from django.shortcuts import render

def home_view(request):
    return render(request, 'HomeView/home.html')

#inventario

def inventory_view(request):
    return render(request, 'InventoryView/inventory.html')

def lista_view(request):
    return render(request, 'InventoryView/lista.html')


#perfiles
def profile_view(request):
    return render(request, 'ProfileView/profile.html')


#reportes
def reports_view(request):
    return render(request, 'ReportsView/reports.html')

#configuracion
def settings_view(request):
    return render(request, 'SettingsView/setting.html')

#notificaciones
def notifications_view(request):
    return render(request, 'NotificationsView/notificacion.html')

#filtros
def filters_view(request):
    return render(request, 'FilterView/filters.html')


def add_material_view(request):
    return render(request, 'InventoryView/agregar.html')

def update_material_view(request):
    return render(request, 'InventoryView/actualizar.html')

def delete_material_view(request):
    return render(request, 'InventoryView/eliminar.html')


def crear_ticket(request):
    return render(request, 'tickets/ver.html')
