from django.shortcuts import render, redirect, get_object_or_404
from .models import *

def home_view(request):
    return render(request, 'HomeView/home.html')

def inventory_view(request):
    return render(request, 'InventoryView/inventory.html')

def lista_view(request):
    materiales = Material.objects.all()  # Obtener todos los materiales desde la base de datos
    return render(request, 'InventoryView/lista.html', {'materiales': materiales})

def add_material_view(request):
    if request.method == 'POST':
        # Crea una nueva instancia del modelo Material
        material = Material()
        material.nombre = request.POST.get('nombre')
        material.descripcion = request.POST.get('descripcion')
        material.unidad_medida = request.POST.get('unidad_medida')
        material.cantidad_disponible = request.POST.get('cantidad_disponible')
        material.stock_minimo = request.POST.get('stock_minimo')
        
        material.save()  # Guarda el nuevo material en la base de datos
        
        return redirect('lista_view')  # Redirige a la vista de lista de materiales después de agregar
    return render(request, 'InventoryView/agregar.html')


def update_material_view(request, id):
    material = get_object_or_404(Material, id=id)  # Obtener el material por ID

    if request.method == 'POST':
        # Actualizar el material con los datos del formulario
        material.nombre = request.POST.get('nombre')
        material.descripcion = request.POST.get('descripcion')  # Agregado para mantener la consistencia
        material.unidad_medida = request.POST.get('unidad_medida')  # Agregado para mantener la consistencia
        material.cantidad_disponible = request.POST.get('cantidad_disponible')  # Asegúrate de que el nombre del campo coincida
        material.stock_minimo = request.POST.get('stock_minimo')  # Asegúrate de que el nombre del campo coincida
        material.save()  # Guardar los cambios
        return redirect('lista_view')  # Redirigir a la lista de materiales después de actualizar

    return render(request, 'InventoryView/editar.html', {'material': material})


def delete_material_view(request, id):
    material = get_object_or_404(Material, id=id)
    if request.method == 'POST':
        material.delete()  # Elimina el material
        return redirect('lista_view')  # Redirige a la lista de materiales después de eliminar
    return render(request, 'InventoryView/eliminar.html', {'material': material})

def stock_alerts_view(request):
    alertas_stock = Material.objects.filter(cantidad_disponible__lt=models.F('stock_minimo'))
    return render(request, 'ReportsView/alertas.html', {'alertas_stock': alertas_stock})

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


def crear_ticket(request):
    if request.method == 'POST':
        usuario = request.POST.get('usuario')
        material_solicitado = request.POST.get('material_solicitado')
        cantidad = request.POST.get('cantidad')
        Ticket.objects.create(usuario=usuario, material_solicitado=material_solicitado, cantidad=cantidad)
        return redirect('lista_tickets')  # Redirige a la lista de tickets después de crear uno
    return render(request, 'tickets/crear.html')

def lista_tickets(request):
    tickets = Ticket.objects.all()
    return render(request, 'tickets/lista.html', {'tickets': tickets})

def ver_ticket(request, ticket_id):
    ticket = Ticket.objects.get(id=ticket_id)
    return render(request, 'tickets/ver.html', {'ticket': ticket})

def eliminar_ticket(request, ticket_id):
    ticket = Ticket.objects.get(id=ticket_id)
    ticket.delete()
    return redirect('lista_tickets')
