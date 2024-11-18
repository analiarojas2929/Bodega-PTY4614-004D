from rest_framework import serializers
from .models import Question, Choice, Material, UnidadMedida


# Serializador para el modelo Question
class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'question_text', 'pub_date']


# Serializador para el modelo Choice
class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'question', 'choice_text', 'votes']


# Serializador para el modelo UnidadMedida
class UnidadMedidaSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnidadMedida
        fields = ['id', 'descripcion']


# Serializador para el modelo Material
class MaterialSerializer(serializers.ModelSerializer):
    # Relación a UnidadMedida usando su descripción
    unidad_medida = serializers.SlugRelatedField(
        queryset=UnidadMedida.objects.all(),
        slug_field='descripcion'
    )

    class Meta:
        model = Material
        fields = ['id', 'nombre', 'descripcion', 'unidad_medida', 'cantidad_disponible', 'stock', 'activo']

    def validate_cantidad_disponible(self, value):
        """Validar que cantidad_disponible no sea negativa."""
        if value < 0:
            raise serializers.ValidationError("La cantidad disponible no puede ser negativa.")
        return value

    def validate_stock(self, value):
        """Validar que stock mínimo sea positivo."""
        if value < 0:
            raise serializers.ValidationError("El stock mínimo debe ser positivo.")
        return value

    def create(self, validated_data):
        """Método para crear un nuevo material."""
        unidad_medida = validated_data.pop('unidad_medida', None)
        if not unidad_medida:
            raise serializers.ValidationError({"unidad_medida": "Unidad de medida es requerida."})

        return Material.objects.create(unidad_medida=unidad_medida, **validated_data)

    def update(self, instance, validated_data):
        """Método para actualizar un material existente."""
        unidad_medida = validated_data.pop('unidad_medida', None)
        if unidad_medida:
            instance.unidad_medida = unidad_medida

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
