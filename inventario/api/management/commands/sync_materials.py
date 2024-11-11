import requests
from django.core.management.base import BaseCommand
from Polls.models import Material, UnidadMedida
from django.conf import settings

API_URL = f"{settings.API_BASE_URL}/materiales/"

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
                unidad_medida, _ = UnidadMedida.objects.get_or_create(descripcion=material_data['unidad_medida'])
                Material.objects.update_or_create(
                    id=material_data['id'],
                    defaults={
                        'nombre': material_data['nombre'],
                        'descripcion': material_data['descripcion'],
                        'unidad_medida': unidad_medida,
                        'cantidad_disponible': material_data['cantidad_disponible'],
                        'stock_minimo': material_data['stock_minimo'],
                        'activo': material_data['activo'],
                    }
                )

            print("Sincronización completada con éxito.")

        except Exception as e:
            print(f"Error al sincronizar materiales: {e}")
