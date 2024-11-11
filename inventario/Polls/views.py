from django.shortcuts import render, redirect, get_object_or_404
from django.db import models
import os
from django.http import JsonResponse
from .models import Material, Ticket, CustomUser
from django.db import transaction
import requests
from django.conf import settings
from .forms import CustomUserForm, TicketForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import logout,authenticate, login
from .roles import ADMINISTRADOR_SISTEMA, ADMINISTRADOR_OBRA, JEFE_OBRA, CAPATAZ, JEFE_BODEGA
from .models import Role
from django.shortcuts import render, redirect
from .models import Material
from .forms import MaterialForm
from .roles import ADMINISTRADOR_OBRA, JEFE_BODEGA, JEFE_OBRA
from django.contrib.auth.models import User
import pdb
from django.contrib.auth.forms import AuthenticationForm
import json
from rest_framework import viewsets
from .models import Question, Choice
from .serializers import QuestionSerializer, ChoiceSerializer

API_BASE_URL = "http://127.0.0.1:8000/api"

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


# Obtener la ruta base del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
@login_required
@user_passes_test(lambda u: has_role_id(u, JEFE_BODEGA) or has_role_id(u, JEFE_OBRA), login_url='/access_denied/')
def lista_view(request):
    materiales_json = []
    json_file_path = os.path.join(settings.BASE_DIR, 'api', 'materiales_data.json')

    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            materiales_json = json.load(file)
    except FileNotFoundError:
        messages.error(request, "Archivo JSON no encontrado.")
    except json.JSONDecodeError:
        messages.error(request, "Error al decodificar el archivo JSON.")
    
    return render(request, 'Modulo_usuario/InventoryView/lista.html', {
        'materiales_json': materiales_json
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
        form = MaterialForm(request.POST)
        if form.is_valid():
            # Guardar en la base de datos
            nuevo_material = form.save()
            
            # Guardar en el archivo JSON
            json_file_path = os.path.join(BASE_DIR, 'api', 'materiales_data.json')
            material_data = {
                "id": nuevo_material.id,
                "nombre": nuevo_material.nombre,
                "descripcion": nuevo_material.descripcion,
                "unidad_medida": nuevo_material.unidad_medida.descripcion,
                "cantidad_disponible": nuevo_material.cantidad_disponible,
                "stock": nuevo_material.stock,
                "activo": nuevo_material.activo
            }

            # Leer el archivo JSON existente y agregar el nuevo material
            if os.path.exists(json_file_path):
                with open(json_file_path, 'r', encoding='utf-8') as file:
                    materiales_json = json.load(file)
            else:
                materiales_json = []

            materiales_json.append(material_data)

            # Guardar de nuevo en el archivo JSON
            with open(json_file_path, 'w', encoding='utf-8') as file:
                json.dump(materiales_json, file, ensure_ascii=False, indent=4)

            return redirect('lista_view')
    else:
        form = MaterialForm()

    return render(request, 'Modulo_usuario/InventoryView/agregar.html', {'form': form})

def actualizar_stock(material_id, nueva_cantidad):
    url = f"{settings.API_BASE_URL}/materiales/{material_id}/"
    data = {'cantidad_disponible': nueva_cantidad}
    response = requests.patch(url, json=data)
    return response.status_code == 200

# Actualizar material (solo accesible por Jefe de Bodega)
# Ruta al archivo JSON
JSON_FILE_PATH = os.path.join(settings.BASE_DIR, 'api', 'materiales_data.json')

@login_required
@user_passes_test(lambda u: has_role_id(u, JEFE_BODEGA), login_url='/access_denied/')
def editar_material(request, material_id):
    # Obtener el material de la base de datos
    material_db = get_object_or_404(Material, id=material_id)
    json_file_path = JSON_FILE_PATH

    if request.method == 'POST':
        form = MaterialForm(request.POST, instance=material_db)
        if form.is_valid():
            # Guardar en la base de datos
            form.save()

            # Cargar el archivo JSON y actualizarlo
            with open(json_file_path, 'r', encoding='utf-8') as file:
                materiales_json = json.load(file)

            # Buscar y actualizar o agregar en el archivo JSON
            material_json = next((m for m in materiales_json if m['id'] == material_id), None)
            if material_json:
                material_json.update({
                    "nombre": form.cleaned_data['nombre'],
                    "descripcion": form.cleaned_data['descripcion'],
                    "unidad_medida": form.cleaned_data['unidad_medida'].descripcion,
                    "cantidad_disponible": form.cleaned_data['cantidad_disponible'],
                    "stock": form.cleaned_data['stock'],
                    "activo": form.cleaned_data['activo']
                })
            else:
                materiales_json.append({
                    "id": material_id,
                    "nombre": form.cleaned_data['nombre'],
                    "descripcion": form.cleaned_data['descripcion'],
                    "unidad_medida": form.cleaned_data['unidad_medida'].descripcion,
                    "cantidad_disponible": form.cleaned_data['cantidad_disponible'],
                    "stock": form.cleaned_data['stock'],
                    "activo": form.cleaned_data['activo']
                })

            # Guardar los cambios en el archivo JSON
            with open(json_file_path, 'w', encoding='utf-8') as file:
                json.dump(materiales_json, file, ensure_ascii=False, indent=4)

            return redirect('lista_view')

    else:
        form = MaterialForm(instance=material_db)

    return render(request, 'Modulo_usuario/InventoryView/editar.html', {
        'form': form,
        'material': material_db
    })
# Eliminar material (solo accesible por Jefe de Bodega)
@login_required
@user_passes_test(lambda u: has_role_id(u, JEFE_BODEGA), login_url='/access_denied/')
def delete_material_view(request, id):
    material = get_object_or_404(Material, id=id)
    if request.method == 'POST':
        material.activo = False
        material.save()

        # Actualizar en el archivo JSON
        try:
            with open(JSON_FILE_PATH, 'r', encoding='utf-8') as file:
                materiales = json.load(file)

            for m in materiales:
                if m['id'] == id:
                    m['activo'] = False
                    break

            with open(JSON_FILE_PATH, 'w', encoding='utf-8') as file:
                json.dump(materiales, file, ensure_ascii=False, indent=4)

        except FileNotFoundError:
            messages.error(request, "Archivo JSON no encontrado.")

        # Actualizar en la API
        api_url = f"{settings.API_BASE_URL}/materiales/{id}/"
        response = requests.patch(api_url, json={'activo': False}, headers={'Content-Type': 'application/json'})
        if response.status_code == 200:
            messages.success(request, "Material desactivado correctamente en la API.")
        else:
            messages.error(request, f"Error al desactivar el material en la API: {response.status_code}")

        return redirect('lista_view')

    return render(request, 'Modulo_usuario/InventoryView/eliminar.html', {'material': material})
# Crear ticket (solo accesible por Jefe de Obra o Jefe de Bodega)
@login_required
@user_passes_test(lambda u: has_role_id(u, JEFE_OBRA) or has_role_id(u, JEFE_BODEGA), login_url='/access_denied/')
def crear_ticket(request):
    try:
        response = requests.get(f'{settings.API_BASE_URL}/materiales/')
        materiales_json = response.json() if response.status_code == 200 else []
    except requests.exceptions.RequestException:
        materiales_json = []
        messages.error(request, "Error al obtener la lista de materiales desde la API.")

    if request.method == 'POST':
        usuario = request.user
        nombre_material = request.POST.get('nombre')
        cantidad = int(request.POST.get('cantidad'))
        estado = request.POST.get('estado')

        materiales = Material.objects.filter(nombre=nombre_material)

        if not materiales.exists():
            messages.error(request, 'El material seleccionado no existe.')
            return redirect('crear_ticket')

        material = materiales.first()

        if material.cantidad_disponible < cantidad:
            messages.error(request, 'No hay suficiente stock disponible.')
            return redirect('crear_ticket')

        try:
            with transaction.atomic():
                material.cantidad_disponible -= cantidad
                material.save()

                ticket = Ticket.objects.create(
                    usuario=usuario,
                    material_solicitado=material,
                    cantidad=cantidad,
                    estado=estado
                )
                messages.success(request, 'Ticket creado exitosamente.')
                print(f"[DEBUG] Ticket creado: {ticket}")

        except Exception as e:
            messages.error(request, f'Error al crear el ticket: {str(e)}')
            print(f"[ERROR] Excepción al crear el ticket: {e}")

        return redirect('lista_tickets')

    return render(request, 'Modulo_usuario/tickets/crear.html', {'materiales': materiales_json})

# Lista de tickets (solo accesible por Jefe de Obra o Jefe de Bodega)
@login_required
@user_passes_test(lambda u: has_role_id(u, JEFE_OBRA) or has_role_id(u, JEFE_BODEGA), login_url='/access_denied/')
def lista_tickets(request):
    tickets = Ticket.objects.all()

    # Filtrar por estado
    estado = request.GET.get('estado')
    if estado:
        tickets = tickets.filter(estado=estado)
    
    return render(request, 'Modulo_usuario/tickets/lista.html', {'tickets': tickets})

@login_required
@user_passes_test(lambda u: has_role_id(u, JEFE_OBRA) or has_role_id(u, JEFE_BODEGA), login_url='/access_denied/')
@login_required
@user_passes_test(lambda u: has_role_id(u, JEFE_OBRA) or has_role_id(u, JEFE_BODEGA), login_url='/access_denied/')
def cobrar_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    material = ticket.material_solicitado

    # Verificar si el ticket ya fue cobrado
    if ticket.estado == 'cobrado':
        messages.warning(request, "El ticket ya ha sido cobrado.")
        return redirect('lista_tickets')

    # Verificar si hay suficiente stock disponible
    if material.cantidad_disponible < ticket.cantidad:
        messages.error(request, 'No hay suficiente stock disponible para cobrar este ticket.')
        return redirect('lista_tickets')

    try:
        # Actualizar la base de datos local dentro de una transacción atómica
        with transaction.atomic():
            material.cantidad_disponible -= ticket.cantidad
            material.save()
            ticket.estado = 'cobrado'
            ticket.save()

            # Actualizar el archivo JSON después de actualizar la base de datos
            actualizar_json_material(material)

        messages.success(request, "Ticket cobrado y stock actualizado correctamente.")

    except Exception as e:
        messages.error(request, f"Error al cobrar el ticket: {str(e)}")

    return redirect('lista_tickets')

def actualizar_json_material(material):
    """Función para actualizar el archivo JSON después de modificar un material."""
    json_file_path = os.path.join(settings.BASE_DIR, 'api', 'materiales_data.json')
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            materiales_json = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        materiales_json = []

    # Buscar el material en el archivo JSON y actualizarlo
    material_json = next((m for m in materiales_json if m['id'] == material.id), None)
    if material_json:
        material_json['cantidad_disponible'] = material.cantidad_disponible
    else:
        # Si no está en el JSON, lo agregamos
        materiales_json.append({
            "id": material.id,
            "nombre": material.nombre,
            "descripcion": material.descripcion,
            "unidad_medida": material.unidad_medida.descripcion,
            "cantidad_disponible": material.cantidad_disponible,
            "stock": material.stock,
            "activo": material.activo
        })

    # Guardar los cambios en el archivo JSON
    with open(json_file_path, 'w', encoding='utf-8') as file:
        json.dump(materiales_json, file, ensure_ascii=False, indent=4)
def actualizar_json_material(material):
    """Función para actualizar el archivo JSON después de modificar un material."""
    json_file_path = os.path.join(settings.BASE_DIR, 'api', 'materiales_data.json')
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            materiales_json = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        materiales_json = []

    # Buscar el material en el archivo JSON y actualizarlo
    material_json = next((m for m in materiales_json if m['id'] == material.id), None)
    if material_json:
        material_json['cantidad_disponible'] = material.cantidad_disponible
    else:
        # Si no está en el JSON, lo agregamos
        materiales_json.append({
            "id": material.id,
            "nombre": material.nombre,
            "descripcion": material.descripcion,
            "unidad_medida": material.unidad_medida.descripcion,
            "cantidad_disponible": material.cantidad_disponible,
            "stock": material.stock,
            "activo": material.activo
        })

    # Guardar los cambios en el archivo JSON
    with open(json_file_path, 'w', encoding='utf-8') as file:
        json.dump(materiales_json, file, ensure_ascii=False, indent=4)


# Ver ticket (solo accesible por Jefe de Obra o Jefe de Bodega)
@login_required
@user_passes_test(lambda u: has_role_id(u, JEFE_OBRA) or has_role_id(u, JEFE_BODEGA), login_url='/access_denied/')
def ver_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    return render(request, 'Modulo_usuario/tickets/ver.html', {'ticket': ticket})


# Eliminar ticket (solo accesible por Jefe de Obra o Jefe de Bodega)
@login_required
def eliminar_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    material = ticket.material_solicitado

    try:
        with transaction.atomic():
            # Revertir la cantidad disponible
            material.cantidad_disponible += ticket.cantidad
            material.save()
            ticket.delete()
            messages.success(request, "Ticket eliminado y cantidad revertida correctamente.")
    except Exception as e:
        messages.error(request, f"Error al eliminar el ticket: {e}")

    return redirect('lista_tickets')

# Vista para alertas de stock (solo accesible por Administrador de Obra)
@login_required
@user_passes_test(lambda u: has_role_id(u, ADMINISTRADOR_OBRA), login_url='/access_denied/')
def stock_alerts_view(request):
    alertas_stock = Material.objects.filter(cantidad_disponible__lt=models.F('stock'))
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

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

class ChoiceViewSet(viewsets.ModelViewSet):
    queryset = Choice.objects.all()
    serializer_class = ChoiceSerializer


@login_required
@user_passes_test(lambda u: has_role_id(u, JEFE_BODEGA), login_url='/access_denied/')
def buscar_material_ajax(request):
    query = request.GET.get('q', '').lower()
    json_file_path = os.path.join(settings.BASE_DIR, 'api', 'materiales_data.json')

    # Verificar si el archivo JSON existe
    if not os.path.exists(json_file_path):
        return JsonResponse({'error': 'Archivo JSON no encontrado'}, status=404)

    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            materiales_json = json.load(file)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Error al decodificar el archivo JSON'}, status=500)

    # Filtrar los materiales según la consulta
    materiales_filtrados = [
        material for material in materiales_json
        if query in material['nombre'].lower()
    ] if query else []

    return JsonResponse({'materiales': materiales_filtrados})
    