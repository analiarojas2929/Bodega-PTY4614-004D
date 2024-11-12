from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Material
import os
import json
import requests
from django.conf import settings

# Ruta al archivo JSON
JSON_FILE_PATH = os.path.join(settings.BASE_DIR, 'api', 'materiales_data.json')

@receiver(post_save, sender=Material)
def sync_material_on_save(sender, instance, created, **kwargs):
    """
    Sincronizar automáticamente cada vez que se crea o actualiza un material.
    """
    material_data = {
        "id": instance.id,
        "nombre": instance.nombre,
        "descripcion": instance.descripcion,
        "unidad_medida": instance.unidad_medida.descripcion,
        "cantidad_disponible": instance.cantidad_disponible,
        "stock": instance.stock,
        "activo": instance.activo
    }

    # Sincronizar con la API
    api_url = f"{settings.API_BASE_URL}/materiales/{instance.id}/"
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.patch(api_url, json=material_data, headers=headers)
        if response.status_code != 200:
            print(f"Error al sincronizar con la API: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error al conectar con la API: {e}")

    # Actualizar el archivo JSON
    try:
        if os.path.exists(JSON_FILE_PATH):
            with open(JSON_FILE_PATH, 'r', encoding='utf-8') as file:
                materiales_json = json.load(file)
        else:
            materiales_json = []

        # Actualizar o agregar el material en el archivo JSON
        for material in materiales_json:
            if material['id'] == instance.id:
                material.update(material_data)
                break
        else:
            materiales_json.append(material_data)

        with open(JSON_FILE_PATH, 'w', encoding='utf-8') as file:
            json.dump(materiales_json, file, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error al actualizar el archivo JSON: {e}")

