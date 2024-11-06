import json
import os
import django

# Configura el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventario.settings')
django.setup()

# Importa el modelo Material
from Polls.models import Material

# Ruta del archivo JSON
json_file_path = 'materiales_data.json'

# Cargar el archivo JSON
with open(json_file_path, 'r', encoding='utf-8') as file:
    materiales_data = json.load(file)

# Guardar cada material en la base de datos
for material_data in materiales_data:
    material, created = Material.objects.get_or_create(
        nombre=material_data['nombre'],
        descripcion=material_data['descripcion'],
        unidad_medida=material_data['unidad_medida'],
        cantidad_disponible=material_data['cantidad_disponible'],
        stock_minimo=material_data['stock_minimo'],
        activo=material_data['activo']
    )
    if created:
        print(f"Material {material.nombre} agregado.")
    else:
        print(f"Material {material.nombre} ya existe.")
