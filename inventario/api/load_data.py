import json
import os
from api.models import Material, UnidadMedida
from django.conf import settings

# Asegúrate de que las unidades de medida existan
unidad_medida_m2, _ = UnidadMedida.objects.get_or_create(descripcion="M2")
unidad_medida_un, _ = UnidadMedida.objects.get_or_create(descripcion="UN")
unidad_medida_rollo, _ = UnidadMedida.objects.get_or_create(descripcion="ROLLO")
unidad_medida_tarro, _ = UnidadMedida.objects.get_or_create(descripcion="TARRO")

# Definir el path al archivo JSON
json_path = os.path.join(settings.BASE_DIR, 'api', 'materiales_data.json')

# Verifica si el archivo JSON existe
if not os.path.exists(json_path):
    raise FileNotFoundError(f"El archivo {json_path} no se encontró.")

# Cargar y guardar los datos en la base de datos
with open(json_path, 'r', encoding='utf-8') as file:
    data = json.load(file)
    for item in data:
        unidad_medida_str = item.pop('unidad_medida')
        
        # Obtener o crear la unidad de medida correspondiente
        unidad_medida, _ = UnidadMedida.objects.get_or_create(descripcion=unidad_medida_str)
        
        # Verificar si el material ya existe en la base de datos
        material, created = Material.objects.update_or_create(
            id=item['id'],
            defaults={
                'nombre': item['nombre'],
                'descripcion': item['descripcion'],
                'unidad_medida': unidad_medida,
                'cantidad_disponible': item['cantidad_disponible'],
                'stock': item['stock'],
                'activo': item['activo']
            }
        )
        if created:
            print(f"Material creado: {material.nombre}")
        else:
            print(f"Material actualizado: {material.nombre}")

print("Datos cargados exitosamente.")
