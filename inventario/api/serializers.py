from rest_framework import serializers
from .models import Material

class MaterialSerializer(serializers.ModelSerializer):
    unidad_medida = serializers.CharField(source="unidad_medida.unidad_medida")

    class Meta:
        model = Material
        fields = ['id', 'nombre', 'descripcion', 'unidad_medida', 'cantidad_disponible', 'stock', 'activo']