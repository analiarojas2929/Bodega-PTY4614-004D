# views.py
from rest_framework import viewsets
from .models import Material
from .serializers import MaterialSerializer
import os
import json
from django.shortcuts import render, redirect
from .models import Material
from .forms import MaterialForm


class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def add_material_view(request):
    if request.method == 'POST':
        form = MaterialForm(request.POST)
        if form.is_valid():
            # Guardar en la base de datos
            nuevo_material = form.save()

            # Guardar en el archivo JSON
            json_file_path = os.path.join(BASE_DIR, 'Polls', 'materiales_data.json')
            material_data = {
                "nombre": nuevo_material.nombre,
                "descripcion": nuevo_material.descripcion,
                "unidad_medida": nuevo_material.unidad_medida.descripcion,
                "cantidad_disponible": nuevo_material.cantidad_disponible,
                "stock_minimo": nuevo_material.stock_minimo,
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

    return render(request, 'Modulo_usuario/InventoryView/agregar_material.html', {'form': form})
