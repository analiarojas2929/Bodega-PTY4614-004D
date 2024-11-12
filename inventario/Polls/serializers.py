from rest_framework import serializers
from .models import Question, Choice, Material


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
    class Meta:
        model = Material
        fields = ['id', 'nombre', 'descripcion', 'unidad_medida', 'cantidad_disponible', 'stock', 'activo']

    def create(self, validated_data):
        """Método para crear un nuevo material"""
        return Material.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """Método para actualizar un material existente"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
