from django.shortcuts import render, redirect, get_object_or_404
from django.db import models
import os
from django.http import JsonResponse,HttpResponse
from .models import Material, Ticket, CustomUser
from django.db import transaction
from django.utils.timezone import make_aware
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

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
import csv
from datetime import datetime

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
        'is_capataz': user.roles.filter(id=CAPATAZ).exists(),
        'can_access_ticket': user.roles.filter(id=CAPATAZ).exists() or user.roles.filter(id=JEFE_OBRA).exists(),
        'can_access_inventario': user.roles.filter(id=JEFE_BODEGA).exists() or user.roles.filter(id=JEFE_OBRA).exists(),
        'can_access_reportes': user.roles.filter(id=ADMINISTRADOR_OBRA).exists(),
        'is_administrador_obra': user.roles.filter(id=ADMINISTRADOR_OBRA).exists(),
        'is_administrador_sistema': user.roles.filter(id=ADMINISTRADOR_SISTEMA).exists(),
        'can_access_list_ticket': user.roles.filter(id=JEFE_BODEGA).exists(),
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
    """
    Vista para listar materiales obtenidos desde la API
    """
    api_url = f"{settings.API_BASE_URL}/materiales/"
    materiales_json = []

    try:
        # Realizar una petición GET a la API para obtener la lista de materiales
        response = requests.get(api_url)
        if response.status_code == 200:
            materiales_json = response.json()
        else:
            messages.error(request, f"Error al obtener datos de la API: {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as e:
        messages.error(request, f"Error al conectar con la API: {e}")

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
    """
    Vista para agregar un nuevo material.
    Se guarda en la base de datos, en la API y en el archivo JSON.
    """
    if request.method == 'POST':
        form = MaterialForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Guardar en la base de datos
                    nuevo_material = form.save()

                    # Estructura de datos para el nuevo material
                    material_data = {
                        "id": nuevo_material.id,
                        "nombre": nuevo_material.nombre,
                        "descripcion": nuevo_material.descripcion,
                        "unidad_medida": nuevo_material.unidad_medida.descripcion,
                        "cantidad_disponible": nuevo_material.cantidad_disponible,
                        "stock": nuevo_material.stock,
                        "activo": nuevo_material.activo
                    }

                    # Guardar en la API
                    api_url = f"{settings.API_BASE_URL}/materiales/"
                    headers = {'Content-Type': 'application/json'}
                    response = requests.post(api_url, json=material_data, headers=headers)

                    if response.status_code == 201:  # Material creado exitosamente en la API
                        # Actualizar el archivo JSON
                        if os.path.exists(JSON_FILE_PATH):
                            with open(JSON_FILE_PATH, 'r', encoding='utf-8') as file:
                                materiales_json = json.load(file)
                        else:
                            materiales_json = []

                        materiales_json.append(material_data)
                        with open(JSON_FILE_PATH, 'w', encoding='utf-8') as file:
                            json.dump(materiales_json, file, ensure_ascii=False, indent=4)

                        messages.success(request, "Material agregado correctamente.")
                    else:
                        messages.error(request, "Error al guardar el material en la API.")

                return redirect('lista_view')

            except Exception as e:
                form.add_error(None, f"Error al guardar el material: {e}")
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
    # Obtener el material por ID o retornar un error 404 si no existe
    material = get_object_or_404(Material, id=material_id)

    # Inicializar el formulario con los datos existentes del material
    if request.method == 'POST':
        form = MaterialForm(request.POST, instance=material)
        if form.is_valid():
            try:
                # Actualizar en la base de datos local
                updated_material = form.save()

                # Preparar los datos para la API
                api_url = f"{settings.API_BASE_URL}/materiales/{material_id}/"
                payload = {
                    "nombre": updated_material.nombre,
                    "descripcion": updated_material.descripcion,
                    "unidad_medida": updated_material.unidad_medida.id,  # Enviar ID de unidad de medida
                    "cantidad_disponible": updated_material.cantidad_disponible,
                    "stock": updated_material.stock,
                    "activo": updated_material.activo
                }

                headers = {'Content-Type': 'application/json'}

                # Realizar la solicitud PATCH a la API
                response = requests.patch(api_url, json=payload, headers=headers)

                if response.status_code == 200:
                    # Actualizar el archivo JSON local
                    actualizar_json_material(updated_material)
                    messages.success(request, 'Material actualizado correctamente en todos los sistemas.')
                else:
                    # Si la API devuelve un error, mostrar el mensaje
                    messages.warning(request, f"Material actualizado localmente, pero hubo un error al actualizar en la API: {response.status_code} - {response.text}")

                return redirect('lista_view')

            except Exception as e:
                # Manejar cualquier excepción que ocurra durante el proceso
                messages.error(request, f"Error al actualizar el material: {str(e)}")
        else:
            messages.error(request, f"Errores en el formulario: {form.errors}")

    else:
        form = MaterialForm(instance=material)

    return render(request, 'Modulo_usuario/InventoryView/editar.html', {
        'form': form,
        'material': material
    })



# Eliminar material (solo accesible por Jefe de Bodega)
@login_required
@user_passes_test(lambda u: has_role_id(u, JEFE_BODEGA), login_url='/access_denied/')
def delete_material_view(request, id):
    """
    Vista para eliminar definitivamente un material tanto de la base de datos como del archivo JSON.
    """
    # Obtener el material de la base de datos
    material = get_object_or_404(Material, id=id)
    
    if request.method == 'POST':
        # Eliminar el material de la base de datos
        material.delete()

        # Eliminar del archivo JSON
        try:
            # Leer el archivo JSON existente
            if os.path.exists(JSON_FILE_PATH):
                with open(JSON_FILE_PATH, 'r', encoding='utf-8') as file:
                    materiales_json = json.load(file)
                
                # Filtrar el material que queremos eliminar
                materiales_json = [m for m in materiales_json if m['id'] != id]

                # Guardar la lista actualizada en el archivo JSON
                with open(JSON_FILE_PATH, 'w', encoding='utf-8') as file:
                    json.dump(materiales_json, file, ensure_ascii=False, indent=4)
            
            messages.success(request, "Material eliminado definitivamente.")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            messages.error(request, f"Error al actualizar el archivo JSON: {e}")

        return redirect('lista_view')

    return render(request, 'Modulo_usuario/InventoryView/eliminar.html', {'material': material})
# Crear ticket (solo accesible por Jefe de Obra  Jefe de Bodega)
@login_required
@user_passes_test(lambda u: has_role_id(u, JEFE_OBRA) or has_role_id(u, CAPATAZ), login_url='/access_denied/')
def crear_ticket(request):
    try:
        # Obtener la lista de materiales desde la API
        response = requests.get(f'{settings.API_BASE_URL}/materiales/')
        materiales_json = response.json() if response.status_code == 200 else []
    except requests.exceptions.RequestException:
        materiales_json = []
        messages.error(request, "Error al obtener la lista de materiales desde la API.")

    if request.method == 'POST':
        usuario = request.user
        try:
            # Obtener la lista de materiales del formulario
            materiales_data = json.loads(request.body).get('materiales', [])

            # Validar que haya materiales seleccionados
            if not materiales_data:
                messages.error(request, 'No se han seleccionado materiales.')
                return JsonResponse({'success': False}, status=400)

            # Crear un ticket por cada material seleccionado
            for material_data in materiales_data:
                nombre_material = material_data.get('nombre')
                cantidad = int(material_data.get('cantidad'))
                estado = material_data.get('estado')

                # Validar que el material existe en la base de datos
                materiales = Material.objects.filter(nombre=nombre_material)
                if not materiales.exists():
                    messages.error(request, f'El material "{nombre_material}" no existe.')
                    continue

                material = materiales.first()

                # Validar si hay suficiente stock disponible
                if material.cantidad_disponible < cantidad and estado == 'cobrado':
                    messages.error(request, f'No hay suficiente stock para "{nombre_material}".')
                    continue

                # Crear el ticket con el estado correspondiente
                Ticket.objects.create(
                    usuario=usuario,
                    material_solicitado=material,
                    cantidad=cantidad,
                    estado=estado
                )

                # Descontar stock solo si el estado es "cobrado"
                if estado == 'cobrado':
                    material.cantidad_disponible -= cantidad
                    material.save()

            messages.success(request, 'Ticket creado exitosamente.')
            return JsonResponse({'success': True})

        except json.JSONDecodeError:
            messages.error(request, 'Error al procesar los datos del formulario.')
            return JsonResponse({'success': False}, status=400)
        except Exception as e:
            messages.error(request, f'Error al crear el ticket: {str(e)}')
            return JsonResponse({'success': False}, status=500)

    return render(request, 'Modulo_usuario/tickets/crear.html', {'materiales': materiales_json})

# Lista de tickets (solo accesible por Jefe de Obra o Jefe de Bodega)
def has_any_role(user, roles):
    return any(user.roles.filter(id=role).exists() for role in roles)

@login_required
@user_passes_test(lambda u: has_any_role(u, [JEFE_OBRA, JEFE_BODEGA, CAPATAZ]), login_url='/access_denied/')
def lista_tickets(request):
    tickets = Ticket.objects.all()

    # Filtrar por estado
    estado = request.GET.get('estado')
    if estado:
        tickets = tickets.filter(estado=estado)
    
    return render(request, 'Modulo_usuario/tickets/lista.html', {'tickets': tickets})

def es_ajax(request):
    """Verifica si la solicitud es AJAX."""
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'

@login_required
@user_passes_test(lambda u: has_role_id(u, JEFE_OBRA) or has_role_id(u, JEFE_BODEGA), login_url='/access_denied/')
def cobrar_ticket(request, ticket_id):
    # Obtener el ticket y el material asociado
    ticket = get_object_or_404(Ticket, id=ticket_id)
    material = ticket.material_solicitado

    # Verificar si el ticket ya fue cobrado
    if ticket.estado == 'cobrado':
        messages.warning(request, "El ticket ya ha sido cobrado anteriormente.")
        return redirect('lista_tickets')

    # Verificar si hay suficiente stock disponible antes de descontar
    if material.cantidad_disponible < ticket.cantidad:
        messages.error(request, 'No hay suficiente stock disponible para cobrar este ticket.')
        return redirect('lista_tickets')

    try:
        with transaction.atomic():
            # Descontar el stock y cambiar el estado del ticket a 'cobrado'
            material.cantidad_disponible -= ticket.cantidad
            material.save()

            ticket.estado = 'cobrado'
            ticket.save(update_fields=['estado'])

        messages.success(request, "Ticket cobrado y stock actualizado correctamente.")
    
    except Exception as e:
        messages.error(request, f"Error al cobrar el ticket: {str(e)}")

    return redirect('lista_tickets')

def actualizar_json_material(material):
    try:
        json_file_path = settings.MATERIALES_JSON_PATH
        if not os.path.exists(json_file_path):
            print(f"[ERROR] Archivo JSON no encontrado: {json_file_path}")
            return False

        with open(json_file_path, 'r+', encoding='utf-8') as file:
            materiales_json = json.load(file)

            # Buscar y actualizar el material en el JSON
            for m in materiales_json:
                if m['id'] == material.id:
                    m.update({
                        "nombre": material.nombre,
                        "descripcion": material.descripcion,
                        "unidad_medida": material.unidad_medida.id,
                        "cantidad_disponible": material.cantidad_disponible,
                        "stock": material.stock,
                        "activo": material.activo
                    })
                    break
            else:
                # Si no se encuentra, agregar el nuevo material
                materiales_json.append({
                    "id": material.id,
                    "nombre": material.nombre,
                    "descripcion": material.descripcion,
                    "unidad_medida": material.unidad_medida.id,
                    "cantidad_disponible": material.cantidad_disponible,
                    "stock": material.stock,
                    "activo": material.activo
                })

            file.seek(0)
            json.dump(materiales_json, file, ensure_ascii=False, indent=4)
            file.truncate()
        
        return True

    except (FileNotFoundError, json.JSONDecodeError, Exception) as e:
        print(f"[ERROR] Error al actualizar el archivo JSON: {e}")
        return False

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
    
    try:
        with transaction.atomic():
            # Remove the line that reverts the material quantity
            ticket.delete()
            messages.success(request, "Ticket eliminado correctamente.")
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
    if request.method == 'POST':
        report_type = request.POST.get('reportType')
        start_date = request.POST.get('startDate')
        end_date = request.POST.get('endDate')

        # Validar y convertir las fechas ingresadas
        try:
            if start_date:
                start_date = make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
            if end_date:
                end_date = make_aware(datetime.strptime(end_date, '%Y-%m-%d'))
        except ValueError:
            return JsonResponse({'error': 'Formato de fecha incorrecto'}, status=400)

        # Manejo para "Inventario Actual"
        if report_type == 'Inventario Actual':
            materiales = Material.objects.select_related('unidad_medida').values(
                'id', 'nombre', 'descripcion', 'cantidad_disponible', 'stock', 'unidad_medida__descripcion', 'activo'
            )
            return JsonResponse({'reportData': list(materiales)})

        # Manejo para "Alertas de Stock Bajo"
        elif report_type == 'Alertas de Stock bajo':
            materiales = Material.objects.select_related('unidad_medida').values(
                'nombre', 'descripcion', 'cantidad_disponible', 'stock', 'unidad_medida__descripcion'
            )
            report_data = [
                {
                    'material': material['nombre'],
                    'descripcion': material['descripcion'],
                    'cantidad_disponible': material['cantidad_disponible'],
                    'stock': material['stock'],
                    'unidad_medida': material['unidad_medida__descripcion'],
                    'alerta_stock': material['cantidad_disponible'] < material['stock']
                }
                for material in materiales if material['cantidad_disponible'] < material['stock']
            ]
            return JsonResponse({'reportData': report_data})

        # Manejo para "Movimientos de Stock"
        elif report_type == 'Movimientos de stock':
            tickets = Ticket.objects.filter(
                estado='cobrado',
                fecha_creacion__range=[start_date, end_date]
            ).values('material_solicitado__nombre', 'cantidad', 'estado', 'fecha_creacion')

            report_data = [
                {
                    'material': ticket['material_solicitado__nombre'],
                    'cantidad': ticket['cantidad'],
                    'estado': ticket['estado'],
                    'fecha_creacion': ticket['fecha_creacion'].strftime('%Y-%m-%d %H:%M:%S')
                }
                for ticket in tickets
            ]
            return JsonResponse({'reportData': report_data})

    return render(request, 'Modulo_usuario/ReportsView/reports.html')
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
            return redirect('Modulo_administrador/usuarios/login_admin.html')  # Cambia esto por el nombre de la vista a la que deseas redirigir
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
    """
    Vista AJAX para buscar materiales por nombre desde la API externa.
    """
    query = request.GET.get('q', '').lower()
    api_url = f"{settings.API_BASE_URL}/materiales/"

    print(f"Consulta de búsqueda: {query}")  # Para depuración

    try:
        response = requests.get(api_url, timeout=5)
        response.raise_for_status()  # Esto lanzará un error si la respuesta no es 200 OK
        materiales_json = response.json()

        print(f"Datos de la API: {materiales_json}")  # Para depuración

        # Filtrar los materiales que coinciden con la consulta
        materiales_filtrados = [
            {
                'id': material['id'],
                'nombre': material['nombre'],
                'unidad_medida': material['unidad_medida'],
                'cantidad_disponible': material['cantidad_disponible']
            }
            for material in materiales_json if query in material['nombre'].lower()
        ]

        print(f"Materiales filtrados: {materiales_filtrados}")  # Para depuración

        return JsonResponse({'materiales': materiales_filtrados})
    
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener datos de la API: {e}")
        return JsonResponse({'error': 'No se pudo obtener la lista de materiales desde la API'}, status=500)
    
from django.http import JsonResponse
from .models import Material

def materiales_list(request):
    query = request.GET.get('search', '').strip().lower()

    # Filtrar los materiales que comienzan con el término de búsqueda
    if query:
        materiales = Material.objects.filter(nombre__istartswith=query, activo=True)
    else:
        materiales = Material.objects.none()  # No devolver nada si no hay consulta

    # Convertir los resultados a JSON
    materiales_filtrados = [
        {
            'id': material.id,
            'nombre': material.nombre,
            'unidad_medida': material.unidad_medida.descripcion,
            'cantidad_disponible': material.cantidad_disponible
        }
        for material in materiales
    ]

    return JsonResponse(materiales_filtrados, safe=False)

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.utils.timezone import make_aware
from datetime import datetime
from .models import Material, Ticket

@login_required
def export_to_pdf(request):
    # Obtener los parámetros del formulario desde la URL
    report_type = request.GET.get('reportType')
    start_date = request.GET.get('startDate')
    end_date = request.GET.get('endDate')

    # Configurar el PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={report_type}_report.pdf'
    p = canvas.Canvas(response, pagesize=letter)
    p.setFont("Helvetica", 12)
    y = 750

    # Validar y convertir las fechas ingresadas
    try:
        if start_date:
            start_date = make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
        if end_date:
            end_date = make_aware(datetime.strptime(end_date, '%Y-%m-%d'))
    except ValueError:
        p.drawString(50, y, 'Formato de fecha incorrecto')
        p.save()
        return response

    # Generar el contenido del PDF basado en el tipo de reporte
    if report_type == 'Inventario Actual':
        materiales = Material.objects.all()
        p.drawString(50, y, 'Reporte de Inventario Actual')
        y -= 30
        for material in materiales:
            p.drawString(50, y, f"{material.nombre} - {material.cantidad_disponible} disponibles")
            y -= 20
            if y < 50:
                p.showPage()
                y = 750

    elif report_type == 'Alertas de Stock bajo':
        materiales = Material.objects.filter(cantidad_disponible__lt=models.F('stock'))
        p.drawString(50, y, 'Reporte de Alertas de Stock Bajo')
        y -= 30
        for material in materiales:
            p.drawString(50, y, f"{material.nombre} - {material.cantidad_disponible} disponibles (Stock mínimo: {material.stock})")
            y -= 20
            if y < 50:
                p.showPage()
                y = 750

    elif report_type == 'Movimientos de stock':
        tickets = Ticket.objects.filter(
            estado='cobrado',
            fecha_creacion__range=[start_date, end_date]
        )
        p.drawString(50, y, 'Reporte de Movimientos de Stock')
        y -= 30
        for ticket in tickets:
            p.drawString(50, y, f"{ticket.material_solicitado.nombre} - {ticket.cantidad} unidades - {ticket.estado}")
            y -= 20
            if y < 50:
                p.showPage()
                y = 750

    else:
        p.drawString(50, y, 'Tipo de reporte no válido')

    p.save()
    return response
