from rest_framework import viewsets, generics
from .models import Material
from .serializers import MaterialSerializer
from .forms import MaterialForm
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.conf import settings
from django.db import transaction
import os
import json

# Ruta al directorio base
BASE_DIR = settings.BASE_DIR

# ViewSet para la API de Material
class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer

# Vista para agregar material y guardar en archivo JSON
def add_material_view(request):
    json_file_path = os.path.join(BASE_DIR, 'api', 'materiales_data.json')

    if request.method == 'POST':
        form = MaterialForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():  # Transacción para asegurarnos de que ambas operaciones se completen
                    # Guardar en la base de datos
                    nuevo_material = form.save()

                    # Estructura de datos para el nuevo material en JSON
                    material_data = {
                        "id": nuevo_material.id,
                        "nombre": nuevo_material.nombre,
                        "descripcion": nuevo_material.descripcion,
                        "unidad_medida": nuevo_material.unidad_medida.descripcion,
                        "cantidad_disponible": nuevo_material.cantidad_disponible,
                        "stock": nuevo_material.stock,
                        "activo": nuevo_material.activo
                    }

                    # Leer el archivo JSON existente o crear una nueva lista
                    if os.path.exists(json_file_path):
                        with open(json_file_path, 'r', encoding='utf-8') as file:
                            materiales_json = json.load(file)
                    else:
                        materiales_json = []

                    # Agregar el nuevo material y guardar en JSON
                    materiales_json.append(material_data)
                    with open(json_file_path, 'w', encoding='utf-8') as file:
                        json.dump(materiales_json, file, ensure_ascii=False, indent=4)

                return redirect('lista_view')

            except Exception as e:
                form.add_error(None, f"Error al guardar el material: {e}")
    else:
        form = MaterialForm()

    return render(request, 'Modulo_usuario/InventoryView/agregar_material.html', {'form': form})


# Búsqueda de materiales en JSON mediante AJAX
def buscar_material_ajax(request):
    query = request.GET.get('q', '').lower()
    json_file_path = os.path.join(BASE_DIR, 'api', 'materiales_data.json')

    # Verificar si el archivo JSON existe y cargarlo
    if not os.path.exists(json_file_path):
        return JsonResponse({'error': 'Archivo JSON no encontrado'}, status=404)

    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            materiales_json = json.load(file)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Error al decodificar el archivo JSON'}, status=500)

    # Filtrar los materiales según la búsqueda
    materiales_filtrados = [
        material for material in materiales_json
        if query in material['nombre'].lower()
    ] if query else []

    return JsonResponse({'materiales': materiales_filtrados})


# Vistas genéricas para Material API
class MaterialListView(generics.ListAPIView):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer

class MaterialDetailView(generics.RetrieveUpdateAPIView):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
