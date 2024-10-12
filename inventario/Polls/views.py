from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from rest_framework import viewsets
from .serializers import MaterialSerializer
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
from .models import CustomUser
from django.http import HttpResponseForbidden
from allauth.socialaccount.helpers import complete_social_login
from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.providers.google.provider import GoogleProvider


def home_view(request):
    return render(request, 'HomeView/home.html')

def inventory_view(request):
    return render(request, 'InventoryView/inventory.html')

def lista_view(request):
    materiales_activos = Material.objects.filter(activo=True)  # Solo materiales activos
    materiales_inactivos = Material.objects.filter(activo=False)  # Solo materiales inactivos
    return render(request, 'InventoryView/lista.html', {
        'materiales': materiales_activos,
        'inactivos': materiales_inactivos
    })

def restore_material_view(request, id):
    material = get_object_or_404(Material, id=id)
    if request.method == 'POST':
        material.activo = True  # Cambia el estado del material a activo
        material.save()
        return redirect('lista_view')  # Redirige a la lista de materiales
    return render(request, 'InventoryView/restaurar.html', {'material': material})

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
        # En lugar de eliminar, marcamos el material como inactivo
        material.activo = False
        material.save()
        return redirect('lista_view')  # Redirige a la lista después de marcarlo como inactivo
    return render(request, 'InventoryView/eliminar.html', {'material': material})

class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer

    # Acción personalizada para eliminar lógicamente
    @action(detail=True, methods=['post'])
    def eliminar(self, request, pk=None):
        material = self.get_object()
        material.activo = False
        material.save()
        return Response({'status': 'Material eliminado lógicamente'})

    # Acción personalizada para restaurar el material
    @action(detail=True, methods=['post'])
    def restaurar(self, request, pk=None):
        material = self.get_object()
        material.activo = True
        material.save()
        return Response({'status': 'Material restaurado'})

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


@login_required
def create_user_view(request):
    # Verifica si el usuario tiene los roles adecuados
    if not request.user.roles.filter(name__in=['Administrador de Sistema', 'Administrador de Obra']).exists():
        return HttpResponseForbidden('No tienes permiso para crear usuarios.')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])  # Configura la contraseña
            user.save()  # Guarda el usuario primero para poder asociar roles
            form.save_m2m()  # Guarda las relaciones ManyToMany (roles)
            return redirect('home')  # Redirige a la página principal después de crear
    else:
        form = CustomUserCreationForm()

    return render(request, 'create_user.html', {'form': form})


@login_required
def some_view(request):
    # Comprobamos si el usuario tiene el rol de 'Administrador de Obra'
    if not request.user.roles.filter(name='Administrador de Obra').exists():
        return HttpResponseForbidden('No tienes acceso a esta sección.')

    # Lógica de la vista si el usuario tiene el rol adecuado
    # Aquí se muestra solo una plantilla de ejemplo
    context = {
        'mensaje': 'Bienvenido a la vista restringida para el Administrador de Obra'
    }
    
    return render(request, 'restricted_view.html', context)

@login_required
def login(request):
    return render(request, 'usuarios/login.html')

def google_login_direct(request):
    # Obtener el proveedor de Google
    provider = GoogleProvider.id
    # Obtenemos la configuración de la aplicación de Google
    app = SocialApp.objects.get(provider=provider)
    # Redirigir a la URL de autenticación de Google
    return redirect(f"https://accounts.google.com/o/oauth2/auth?client_id={app.client_id}&redirect_uri=http://127.0.0.1:8000/accounts/google/login/callback/&scope=openid%20email%20profile&response_type=code")