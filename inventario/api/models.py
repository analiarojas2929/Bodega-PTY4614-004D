from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

# Create your models here.
# Modelo para los Materiales
class Material(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    unidad_medida = models.ForeignKey('UnidadMedida', on_delete=models.CASCADE, default=1)
    cantidad_disponible = models.IntegerField()
    stock_minimo = models.IntegerField()
    activo = models.BooleanField(default=True)  # Campo para eliminación lógica

    def clean(self):
        if self.cantidad_disponible < 0:
            raise ValidationError('La cantidad disponible no puede ser negativa.')

    def __str__(self):
        return self.nombre

# Modelo para Unidad de Medida
class UnidadMedida(models.Model):
    descripcion = models.CharField(max_length=50)

    def __str__(self):
        return self.descripcion
