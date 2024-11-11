import os
import django

# Configura el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventario.settings')
django.setup()

from api.models import UnidadMedida

# Crear las unidades de medida
UnidadMedida.objects.get_or_create(descripcion="M2")
UnidadMedida.objects.get_or_create(descripcion="UN")
UnidadMedida.objects.get_or_create(descripcion="ROLLO")
UnidadMedida.objects.get_or_create(descripcion="TARRO")

print("Unidades de medida inicializadas.")

