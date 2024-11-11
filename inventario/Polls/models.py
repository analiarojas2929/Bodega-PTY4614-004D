from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

class Role(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    roles = models.ManyToManyField(Role,  related_name='users') 
    def __str__(self):
        return self.username 
    

# Modelo para los Materiales
class Material(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    unidad_medida = models.ForeignKey('UnidadMedida', on_delete=models.CASCADE)
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

# Modelo para Estado de Tickets
class EstadoTicket(models.Model):
    descripcion = models.TextField()
    fecha_salida = models.DateField(null=True, blank=True)
    fecha_entrega = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.descripcion

from django.utils.timezone import now

class Ticket(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('cobrado', 'Cobrado'),
    ]
    
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    material_solicitado = models.ForeignKey(Material, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    fecha_creacion = models.DateTimeField(default=now)  # Cambiado para permitir un valor predeterminado

    def __str__(self):
        return f"{self.material_solicitado.nombre} - {self.cantidad} unidades"

# Modelo para los Proveedores
class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    contacto = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    email = models.EmailField(max_length=100)
    direccion = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre

# Modelo para Estado de Pedidos
class EstadoPedido(models.Model):
    descripcion = models.TextField()

    def __str__(self):
        return self.descripcion

# Modelo para los Pedidos
class Pedido(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pedido = models.DateField()
    fecha_entrega = models.DateField()
    estado = models.ForeignKey(EstadoPedido, on_delete=models.CASCADE)

    def __str__(self):
        return f"Pedido {self.id} - {self.proveedor.nombre}"

# Modelo para Tipo de Reportes
class TipoReporte(models.Model):
    descripcion = models.TextField()

    def __str__(self):
        return self.descripcion

# Modelo para los Reportes
class Reporte(models.Model):
    usuario = models.ForeignKey('CustomUser', on_delete=models.CASCADE)  # Referencia directa a CustomUser
    tipo_reporte = models.ForeignKey(TipoReporte, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    fecha_generacion = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Reporte {self.id} - {self.tipo_reporte.descripcion}"





class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return self.question_text

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text