import json
import os
from django.core.management.base import BaseCommand
from api.models import Material, UnidadMedida
from django.conf import settings

class Command(BaseCommand):
    help = "Sincroniza los materiales desde el archivo JSON a la base de datos"

    def handle(self, *args, **kwargs):
        # Ruta al archivo JSON
        json_file_path = os.path.join(settings.BASE_DIR, 'api', 'materiales_data.json')
        
        # Verificar si el archivo JSON existe
        if not os.path.exists(json_file_path):
            self.stdout.write(self.style.ERROR(f"El archivo {json_file_path} no se encontró."))
            return

        # Asegúrate de que las unidades de medida existen en la base de datos
        unidades_medida = {
            "M2": UnidadMedida.objects.get_or_create(descripcion="M2")[0],
            "UN": UnidadMedida.objects.get_or_create(descripcion="UN")[0],
            "ROLLO": UnidadMedida.objects.get_or_create(descripcion="ROLLO")[0],
            "TARRO": UnidadMedida.objects.get_or_create(descripcion="TARRO")[0],
            "LITRO": UnidadMedida.objects.get_or_create(descripcion="LITRO")[0]
        }

        # Leer y cargar el archivo JSON
        with open(json_file_path, 'r', encoding='utf-8') as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError as e:
                self.stdout.write(self.style.ERROR(f"Error al decodificar el archivo JSON: {e}"))
                return

        # Sincronizar los datos en la base de datos
        for item in data:
            unidad_medida_str = item.get('unidad_medida')
            unidad_medida = unidades_medida.get(unidad_medida_str)
            
            if not unidad_medida:
                self.stdout.write(self.style.WARNING(f"Unidad de medida no encontrada: {unidad_medida_str}"))
                continue

            # Crear o actualizar el material
            Material.objects.update_or_create(
                id=item['id'],
                defaults={
                    'nombre': item['nombre'],
                    'descripcion': item['descripcion'],  # Asegúrate de que el campo descripción está presente
                    'unidad_medida': unidad_medida,
                    'cantidad_disponible': item['cantidad_disponible'],
                    'stock': item['stock'],
                    'activo': item['activo']
                }
            )

        self.stdout.write(self.style.SUCCESS("Sincronización completada correctamente."))

