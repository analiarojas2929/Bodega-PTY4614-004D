from django.shortcuts import render, redirect, get_object_or_404
from django.db import models
from .models import Material, Ticket, CustomUser
from .forms import CustomUserForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import logout,authenticate, login
from .roles import ADMINISTRADOR_SISTEMA, ADMINISTRADOR_OBRA, JEFE_OBRA, CAPATAZ, JEFE_BODEGA
from .models import Role
from .roles import ADMINISTRADOR_OBRA, JEFE_BODEGA, JEFE_OBRA
from django.contrib.auth.models import User
import pdb
from django.contrib.auth.forms import AuthenticationForm
import json

def has_role_id(user, role_id):
    return user.roles.filter(id=role_id).exists()

# Vista principal
def home_view(request):
    context = get_role_context(request.user)
    return render(request, 'Modulo_usuario/HomeView/home.html', context)

def get_role_context(user):
    return {
        'is_jefe_bodega': user.roles.filter(id=JEFE_BODEGA).exists(),
        'is_jefe_obra': user.roles.filter(id=JEFE_OBRA).exists(),
        'can_access_ticket': user.roles.filter(id=JEFE_BODEGA).exists() or user.roles.filter(id=JEFE_OBRA).exists(),
        'can_access_inventario': user.roles.filter(id=JEFE_BODEGA).exists() or user.roles.filter(id=JEFE_OBRA).exists(),
        'can_access_reportes': user.roles.filter(id=ADMINISTRADOR_OBRA).exists(),
        'is_administrador_obra': user.roles.filter(id=ADMINISTRADOR_OBRA).exists(),
        'is_administrador_sistema': user.roles.filter(id=ADMINISTRADOR_SISTEMA).exists(),
    }


# Vista de inventario (solo accesible por Jefe de Bodega, Role ID = 5)
@login_required
@user_passes_test(lambda u: has_role_id(u, JEFE_BODEGA) or has_role_id(u, JEFE_OBRA), login_url='/access_denied/')
def inventory(request):
    context = get_role_context(request.user)
    return render(request, 'Modulo_usuario/InventoryView/inventory.html', context)


# Lista de materiales activos e inactivos (solo accesible por Jefe de Bodega)
@login_required
@user_passes_test(lambda u: has_role_id(u, JEFE_BODEGA) or has_role_id(u, JEFE_OBRA), login_url='/access_denied/')
def lista_view(request):
    # Obtener materiales activos e inactivos desde la base de datos
    materiales_activos = Material.objects.filter(activo=True)
    materiales_inactivos = Material.objects.filter(activo=False)

    # Leer el archivo JSON
    json_file_path = 'Polls/materiales_data.json'
    with open(json_file_path, 'r', encoding='utf-8') as file:
        materiales_json = json.load(file)

    # Pasar los materiales de la base de datos y del JSON a la plantilla
    return render(request, 'Modulo_usuario/InventoryView/lista.html', {
        'materiales': materiales_activos,
        'inactivos': materiales_inactivos,
        'materiales_json': materiales_json  # Añadir materiales desde el JSON
    })

@login_required(login_url='/admin_login/')
@user_passes_test(lambda u: has_role_id(u, ADMINISTRADOR_SISTEMA), login_url='/access_denied/')
def home_admin(request):
    return render(request, 'Modulo_administrador/usuarios/home_admin.html')


@login_required(login_url='/admin_login/')
def restricted_view(request):
    usuario = request.user
    roles = usuario.roles.all()  # Obtener los roles del usuario

    context = {
        'usuario': usuario,
        'roles': roles,
        'is_administrador_obra': has_role_id(usuario, ADMINISTRADOR_OBRA),
        'is_jefe_bodega': has_role_id(usuario, JEFE_BODEGA),
        'is_jefe_obra': has_role_id(usuario, JEFE_OBRA),
        'is_administrador_sistema': has_role_id(usuario, ADMINISTRADOR_SISTEMA),
    }
    return render(request, 'Modulo_administrador/usuarios/restricted_view.html', context)



@login_required(login_url='/admin_login/')
@user_passes_test(lambda u: has_role_id(u, ADMINISTRADOR_SISTEMA), login_url='/access_denied/')
def redirect_home_administrador(request):
    """
    Vista restringida que muestra detalles del usuario autenticado.
    Solo usuarios autenticados pueden acceder a esta vista.
    """
    usuario = request.user
    roles = usuario.roles.all()  # Obtener los roles del usuario

    # Depuración: Imprimir roles en la consola (opcional)
    print(f"Usuario: {usuario.username}, Roles: {roles}")

    context = {
        'usuario': usuario,
        'roles': roles,
        'mensaje': 'Bienvenido a la vista restringida'
    }
    return render(request, 'Modulo_administrador/usuarios/restricted_view.html', context)
def custom_login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if has_role_id(user, ADMINISTRADOR_SISTEMA):  # Verifica el rol
                return redirect('admin_user_list')  # Redirige al menú de administrador
            else:
                return redirect('home')  # Redirige a la página de inicio para otros roles
    else:
        form = AuthenticationForm()
    return render(request, 'Modulo_administrador/usuarios/login_admin.html', {'form': form})

# Restaurar material inactivo (solo accesible por Jefe de Bodega)
@login_required
@user_passes_test(lambda u: has_role_id(u, JEFE_BODEGA), login_url='/access_denied/')
def restore_material_view(request, id):
    material = get_object_or_404(Material, id=id)
    if request.method == 'POST':
        material.activo = True
        material.save()
        return redirect('lista_view')
    return render(request, 'Modulo_usuario/InventoryView/restaurar.html', {'material': material})


# Agregar material (solo accesible por Jefe de Bodega)
@login_required
@user_passes_test(lambda u: has_role_id(u, JEFE_BODEGA), login_url='/access_denied/')
def add_material_view(request):
    if request.method == 'POST':
        material = Material(
            nombre=request.POST.get('nombre'),
            descripcion=request.POST.get('descripcion'),
            unidad_medida=request.POST.get('unidad_medida'),
            cantidad_disponible=request.POST.get('cantidad_disponible'),
            stock_minimo=request.POST.get('stock_minimo')
        )
        material.save()
        return redirect('lista_view')
    return render(request, 'Modulo_usuario/InventoryView/agregar.html')


# Actualizar material (solo accesible por Jefe de Bodega)
@login_required
@user_passes_test(lambda u: has_role_id(u, JEFE_BODEGA), login_url='/access_denied/')
def update_material_view(request, id):
    material = get_object_or_404(Material, id=id)
    if request.method == 'POST':
        material.nombre = request.POST.get('nombre')
        material.descripcion = request.POST.get('descripcion')
        material.unidad_medida = request.POST.get('unidad_medida')
        material.cantidad_disponible = request.POST.get('cantidad_disponible')
        material.stock_minimo = request.POST.get('stock_minimo')
        material.save()
        return redirect('lista_view')
    return render(request, 'Modulo_usuario/InventoryView/editar.html', {'material': material})


# Eliminar material (solo accesible por Jefe de Bodega)
@login_required
@user_passes_test(lambda u: has_role_id(u, JEFE_BODEGA), login_url='/access_denied/')
def delete_material_view(request, id):
    material = get_object_or_404(Material, id=id)
    if request.method == 'POST':
        material.activo = False
        material.save()
        return redirect('lista_view')
    return render(request, 'Modulo_usuario/InventoryView/eliminar.html', {'material': material})


# Crear ticket (solo accesible por Jefe de Obra o Jefe de Bodega)
@login_required
@user_passes_test(lambda u: has_role_id(u, JEFE_OBRA) or has_role_id(u, JEFE_BODEGA), login_url='/access_denied/')
def crear_ticket(request):
    if request.method == 'POST':
        Ticket.objects.create(
            usuario=request.POST.get('usuario'),
            material_solicitado=request.POST.get('material_solicitado'),
            cantidad=request.POST.get('cantidad')
        )
        return redirect('lista_tickets')
    return render(request, 'Modulo_usuario/tickets/crear.html')


# Lista de tickets (solo accesible por Jefe de Obra o Jefe de Bodega)
@login_required
@user_passes_test(lambda u: has_role_id(u, JEFE_OBRA) or has_role_id(u, JEFE_BODEGA), login_url='/access_denied/')
def lista_tickets(request):
    tickets = Ticket.objects.all()
    return render(request, 'Modulo_usuario/tickets/lista.html', {'tickets': tickets})

# Ver ticket (solo accesible por Jefe de Obra o Jefe de Bodega)
@login_required
@user_passes_test(lambda u: has_role_id(u, JEFE_OBRA) or has_role_id(u, JEFE_BODEGA), login_url='/access_denied/')
def ver_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    return render(request, 'Modulo_usuario/tickets/ver.html', {'ticket': ticket})


# Eliminar ticket (solo accesible por Jefe de Obra o Jefe de Bodega)
@login_required
@user_passes_test(lambda u: has_role_id(u, JEFE_OBRA) or has_role_id(u, JEFE_BODEGA), login_url='/access_denied/')
def eliminar_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    ticket.delete()
    return redirect('lista_tickets')


# Vista para alertas de stock (solo accesible por Administrador de Obra)
@login_required
@user_passes_test(lambda u: has_role_id(u, ADMINISTRADOR_OBRA), login_url='/access_denied/')
def stock_alerts_view(request):
    alertas_stock = Material.objects.filter(cantidad_disponible__lt=models.F('stock_minimo'))
    return render(request, 'Modulo_usuario/ReportsView/alertas.html', {'alertas_stock': alertas_stock})


# Vista de reportes (solo accesible por Administradores de Obra)
@login_required
@user_passes_test(lambda u: has_role_id(u, ADMINISTRADOR_OBRA), login_url='/access_denied/')
def reports_view(request):
    reportes = []  # Aquí podrías cargar los reportes desde la base de datos
    return render(request, 'Modulo_usuario/ReportsView/reports.html', {'reportes': reportes})

def user_login(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Verificar si el nombre de usuario existe
        if not CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'El usuario ingresado no existe.')
        else:
            # Validar la autenticación del usuario
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Inicio de sesión exitoso.')
                
                # Redirigir según el rol del usuario
                if has_role_id(user, ADMINISTRADOR_SISTEMA):
                    return redirect('admin_user_list')
                else:
                    return redirect('home')
            else:
                messages.error(request, 'Contraseña incorrecta.')

    return render(request, 'Modulo_usuario/usuarios/login.html', {'form': form})
# Crear usuario
# En views.py del administrador de sistema
def create_user(request):
    if request.method == 'POST':
        form = CustomUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario creado con éxito.")
            return redirect('login_admin')  # Cambia esto por el nombre de la vista a la que deseas redirigir
    else:
        form = CustomUserForm()
    
    return render(request, 'Modulo_administrador/usuarios/create_user.html', {'form': form})  # Asegúrate de cambiar 'tu_template.html' por el nombre real de tu plantilla
# Cerrar sesión y redirigir al login
def custom_logout_view(request):
    logout(request)
    return redirect('login')


# Vista de acceso denegado
def access_denied_view(request):
    return render(request, 'Modulo_usuario/errors/access_denied.html')


# Crear roles predeterminados
def create_roles(request):
    roles = [
        {'id': ADMINISTRADOR_SISTEMA, 'name': 'Administrador de sistema'},
        {'id': ADMINISTRADOR_OBRA, 'name': 'Administrador de obra'},
        {'id': JEFE_OBRA, 'name': 'Jefe de obra'},
        {'id': CAPATAZ, 'name': 'Capataz'},
        {'id': JEFE_BODEGA, 'name': 'Jefe de Bodega'},
    ]
    
    for role_data in roles:
        Role.objects.get_or_create(id=role_data['id'], defaults={'name': role_data['name']})
    
    return redirect('home')


# Vista para listar usuarios con sus roles en el menú de administrador
@login_required
@user_passes_test(lambda u: has_role_id(u, ADMINISTRADOR_SISTEMA), login_url='/access_denied/')
def admin_user_list(request):
    users = CustomUser.objects.prefetch_related('roles').all()  # Asegúrate de que 'roles' sea la relación correcta
    context = {
        'users': users
    }
    return render(request, 'Modulo_administrador/menu_administrador/user_list.html', context)
def lista_usuarios(request):
    users = CustomUser.objects.all()
    return render(request, 'Modulo_administrador/menu_administrador/user_list.html', {'users': users})

@login_required
def inactivar_usuario(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_active = False
    user.save()
    return redirect('lista_usuarios')

@login_required
def editar_usuario(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)
    if request.method == 'POST':
        form = CustomUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('lista_usuarios')
    else:
        form = CustomUserForm(instance=user)
    return render(request, 'Modulo_administrador/menu_administrador/editar_user.html', {'form': form})
@login_required
def crear_usuario(request):
    if request.method == 'POST':
        form = CustomUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_usuarios')
    else:
        form = CustomUserForm()
    return render(request, 'Modulo_administrador/usuarios/create_user.html', {'form': form})

@login_required
def activar_usuario(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_active = True
    user.save()
    return redirect('lista_usuarios')