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

# Serializador para el modelo Material
class MaterialSerializer(serializers.ModelSerializer):
    unidad_medida = serializers.CharField(source='unidad_medida.descripcion', required=False)

    class Meta:
        model = Material
        fields = ['id', 'nombre', 'descripcion', 'unidad_medida', 'cantidad_disponible', 'stock', 'activo']

    def create(self, validated_data):
        """Método para crear un nuevo material"""
        unidad_medida_data = validated_data.pop('unidad_medida', None)
        if unidad_medida_data:
            unidad_medida_obj, _ = UnidadMedida.objects.get_or_create(descripcion=unidad_medida_data['descripcion'])
            validated_data['unidad_medida'] = unidad_medida_obj

        return Material.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """Método para actualizar un material existente"""
        # Manejar el campo `unidad_medida` si se proporciona
        unidad_medida_data = validated_data.pop('unidad_medida', None)
        if unidad_medida_data:
            unidad_medida_obj, _ = UnidadMedida.objects.get_or_create(descripcion=unidad_medida_data['descripcion'])
            instance.unidad_medida = unidad_medida_obj

        # Actualizar otros campos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
