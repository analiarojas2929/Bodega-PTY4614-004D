import json
import os
from api.models import Material, UnidadMedida

# Asegúrate de que las unidades de medida existan
UnidadMedida.objects.get_or_create(descripcion="M2")
UnidadMedida.objects.get_or_create(descripcion="UN")
UnidadMedida.objects.get_or_create(descripcion="ROLLO")
UnidadMedida.objects.get_or_create(descripcion="TARRO")

# Continuar con la carga de datos
BASE_DIR = os.getcwd()
json_path = os.path.join(BASE_DIR, 'api', 'materiales_data.json')

if not os.path.exists(json_path):
    raise FileNotFoundError(f"El archivo {json_path} no se encontró.")

with open(json_path, 'r', encoding='utf-8') as file:
    data = json.load(file)
    for item in data:
        unidad_medida_str = item.pop('unidad_medida')
        unidad_medida, _ = UnidadMedida.objects.get_or_create(descripcion=unidad_medida_str)
        Material.objects.create(unidad_medida=unidad_medida, **item)

print("Datos cargados exitosamente")
