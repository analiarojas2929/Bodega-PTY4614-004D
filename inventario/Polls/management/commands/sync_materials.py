import requests
from django.core.management.base import BaseCommand
from Polls.models import Material, UnidadMedida
from django.conf import settings

API_URL = f"{settings.API_BASE_URL}/materiales/"

# Lista de materiales a excluir
MATERIALES_EXCLUIDOS = ['madera', 'palo']

class Command(BaseCommand):
    help = 'Sincronizar materiales con la API'

    def handle(self, *args, **kwargs):
        print("Sincronizando materiales desde la API...")
        try:
            response = requests.get(API_URL)
            if response.status_code != 200:
                print(f"Error al obtener datos de la API: {response.status_code}")
                return

            materiales_api = response.json()

            for material_data in materiales_api:
                # Normalizar el nombre del material (eliminar espacios y convertir a minúsculas)
                nombre_normalizado = material_data['nombre'].strip().lower()

                # Excluir materiales no deseados
                if nombre_normalizado in [m.lower() for m in MATERIALES_EXCLUIDOS]:
                    print(f"Material excluido: {material_data['nombre']}")
                    continue

                # Validar la unidad de medida
                if not material_data.get('unidad_medida'):
                    print(f"Material '{material_data['nombre']}' tiene una unidad de medida inválida.")
                    continue

                # Obtener o crear la unidad de medida
                unidad_medida, _ = UnidadMedida.objects.get_or_create(
                    descripcion=material_data['unidad_medida']
                )

                # Actualizar o crear el material en la base de datos
                Material.objects.update_or_create(
                    id=material_data['id'],
                    defaults={
                        'nombre': material_data['nombre'],
                        'descripcion': material_data['descripcion'],
                        'unidad_medida': unidad_medida,
                        'cantidad_disponible': material_data['cantidad_disponible'],
                        'stock': material_data['stock'],
                        'activo': material_data['activo'],
                    }
                )
                print(f"Material sincronizado: {material_data['nombre']}")

            print("Sincronización completada con éxito.")

        except Exception as e:
            print(f"Error al sincronizar materiales: {e}")
