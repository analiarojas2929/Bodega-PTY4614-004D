from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

# Create your models here.
# Modelo para los Materiales
class Material(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    unidad_medida = models.ForeignKey('UnidadMedida', on_delete=models.CASCADE)
    cantidad_disponible = models.IntegerField()
    stock= models.IntegerField()
    activo = models.BooleanField(default=True)  # Campo para eliminación lógica

    def clean(self):
        if self.cantidad_disponible < 0:
            raise ValidationError('La cantidad disponible no puede ser negativa.')

    def __str__(self):
        return self.nombre

# Modelo para Unidad de Medida
# Modelo para Unidad de Medida con descripción adicional
class UnidadMedida(models.Model):
    unidad_medida = models.CharField(max_length=10, choices=[
        ('M2', 'M2'),
        ('UN', 'UN'),
        ('ROLLO', 'ROLLO'),
        ('TARRO', 'TARRO'),
        ('LITRO', 'LITRO'),
    ],
    default='UN')
    descripcion = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        unique_together = ('unidad_medida', 'descripcion')  # Evita duplicados

    def __str__(self):
        return f"{self.unidad_medida} - {self.descripcion}" if self.descripcion else self.unidad_medida
