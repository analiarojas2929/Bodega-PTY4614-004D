from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

class Material(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    unidad_medida = models.CharField(max_length=50)
    cantidad_disponible = models.DecimalField(max_digits=10, decimal_places=2)
    stock_minimo = models.DecimalField(max_digits=10, decimal_places=2)
    activo = models.BooleanField(default=True)  # Nuevo campo para eliminación lógica

    def __str__(self):
        return self.nombre


class UnidadMedida(models.Model):
    descripcion = models.CharField(max_length=50)

    def __str__(self):
        return self.descripcion


class EstadoTicket(models.Model):
    descripcion = models.TextField()
    fecha_salida = models.DateField(null=True, blank=True)
    fecha_entrega = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.descripcion


class Ticket(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
    ]

    fecha = models.DateTimeField(default=timezone.now)
    usuario = models.CharField(max_length=100)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='pendiente')
    material_solicitado = models.CharField(max_length=255, null=True, blank=True)
    cantidad = models.IntegerField(default=0)

    def __str__(self):
        return f'Ticket #{self.id} - {self.estado}'


class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    contacto = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    email = models.EmailField(max_length=100)
    direccion = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre


class EstadoPedido(models.Model):
    descripcion = models.TextField()

    def __str__(self):
        return self.descripcion


class Pedido(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pedido = models.DateField()
    fecha_entrega = models.DateField()
    estado = models.ForeignKey(EstadoPedido, on_delete=models.CASCADE)

    def __str__(self):
        return f"Pedido {self.id} - {self.proveedor.nombre}"


class TipoReporte(models.Model):
    descripcion = models.TextField()

    def __str__(self):
        return self.descripcion


class Reporte(models.Model):
    usuario = models.ForeignKey('CustomUser', on_delete=models.CASCADE)  # Cambié la referencia de 'Usuario' a 'CustomUser'
    tipo_reporte = models.ForeignKey(TipoReporte, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    fecha_generacion = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Reporte {self.id} - {self.tipo_reporte.descripcion}"


class Role(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    roles = models.ManyToManyField(Role, related_name='users')