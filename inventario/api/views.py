from rest_framework import viewsets, generics, status, authentication, permissions
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.conf import settings
from django.db import transaction
import os
import json
from Polls.models import Material, UnidadMedida
from api.serializers import MaterialSerializer
from Polls.forms import MaterialForm

BASE_DIR = settings.BASE_DIR


### 1. ViewSet para la API de Material
class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    authentication_classes = [authentication.SessionAuthentication, authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        """Eliminar lógicamente un material usando el método DELETE"""
        try:
            material = self.get_object()
            material.activo = False
            material.save()
            return Response({"message": "Material eliminado lógicamente"}, status=status.HTTP_200_OK)
        except Material.DoesNotExist:
            return Response({"error": "Material no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['patch'])
    def delete_material(self, request, pk=None):
        """Eliminación lógica de un material usando PATCH"""
        try:
            material = self.get_object()
            material.activo = False
            material.save()
            return Response({"message": "Material eliminado lógicamente"}, status=status.HTTP_200_OK)
        except Material.DoesNotExist:
            return Response({"error": "Material no encontrado"}, status=status.HTTP_404_NOT_FOUND)


### 2. Vista para agregar un nuevo material y guardarlo en un archivo JSON
def add_material_view(request):
    json_file_path = os.path.join(BASE_DIR, 'api', 'materiales_data.json')

    if not os.path.exists(json_file_path):
        # Crear el archivo JSON si no existe
        with open(json_file_path, 'w', encoding='utf-8') as file:
            json.dump([], file, ensure_ascii=False, indent=4)

    if request.method == 'POST':
        form = MaterialForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    nuevo_material = form.save()

                    material_data = {
                        "id": nuevo_material.id,
                        "nombre": nuevo_material.nombre,
                        "descripcion": nuevo_material.descripcion,
                        "unidad_medida": nuevo_material.unidad_medida.descripcion,
                        "cantidad_disponible": nuevo_material.cantidad_disponible,
                        "stock": nuevo_material.stock,
                        "activo": nuevo_material.activo
                    }

                    # Leer y actualizar el archivo JSON
                    with open(json_file_path, 'r', encoding='utf-8') as file:
                        materiales_json = json.load(file)

                    materiales_json.append(material_data)

                    with open(json_file_path, 'w', encoding='utf-8') as file:
                        json.dump(materiales_json, file, ensure_ascii=False, indent=4)

                return redirect('lista_view')

            except Exception as e:
                form.add_error(None, f"Error al guardar el material: {e}")
    else:
        form = MaterialForm()

    return render(request, 'Modulo_usuario/InventoryView/agregar.html', {'form': form})


### 3. Vista para buscar materiales en archivo JSON mediante AJAX
def buscar_material_ajax(request):
    query = request.GET.get('q', '').strip().lower()
    json_file_path = os.path.join(BASE_DIR, 'api', 'materiales_data.json')

    if not os.path.exists(json_file_path):
        return JsonResponse({'error': 'Archivo JSON no encontrado'}, status=404)

    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            materiales_json = json.load(file)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Error al decodificar el archivo JSON'}, status=500)

    materiales_filtrados = [
        {
            'id': material['id'],
            'nombre': material['nombre'],
            'unidad_medida': material['unidad_medida'],
            'cantidad_disponible': material['cantidad_disponible']
        }
        for material in materiales_json if query in material['nombre'].lower()
    ] if query else []

    return JsonResponse({'materiales': materiales_filtrados})


### 4. Vista genérica para listar materiales
class MaterialListView(generics.ListAPIView):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer


### 5. Vista genérica para obtener y actualizar un material por ID
class MaterialDetailView(generics.RetrieveUpdateAPIView):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer


### 6. Vista para sincronizar materiales desde un archivo JSON usando un API endpoint
@api_view(['GET', 'POST'])
def sync_materiales(request):
    if request.method == 'GET':
        materiales = Material.objects.filter(activo=True)
        serializer = MaterialSerializer(materiales, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        data = request.data
        errores = []
        try:
            with transaction.atomic():
                for material_data in data:
                    if not all(key in material_data for key in ['id', 'nombre', 'unidad_medida', 'cantidad_disponible', 'stock', 'activo']):
                        errores.append(f"Datos incompletos para material: {material_data.get('nombre', 'Desconocido')}")
                        continue

                    unidad_medida, _ = UnidadMedida.objects.get_or_create(
                        descripcion=material_data['unidad_medida']
                    )
                    Material.objects.update_or_create(
                        id=material_data['id'],
                        defaults={
                            'nombre': material_data['nombre'],
                            'descripcion': material_data['descripcion'],
                            'unidad_medida': unidad_medida,
                            'cantidad_disponible': material_data['cantidad_disponible'],
                            'stock': material_data['stock'],
                            'activo': material_data['activo']
                        }
                    )
            if errores:
                return Response({"message": "Sincronización parcial", "errores": errores}, status=status.HTTP_206_PARTIAL_CONTENT)
            return Response({"message": "Sincronización completada"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
