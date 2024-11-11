from rest_framework import serializers
from .models import Material

class MaterialSerializer(serializers.ModelSerializer):
    unidad_medida = serializers.CharField(source="unidad_medida.descripcion")  # Asegúrate de que este campo sea correcto

    class Meta:
        model = Material
        fields = ['id', 'nombre', 'descripcion', 'unidad_medida', 'cantidad_disponible', 'stock', 'activo']
