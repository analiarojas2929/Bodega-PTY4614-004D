from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.hashers import make_password
from .models import CustomUser, Role, Material, Ticket, UnidadMedida

from django import forms
from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from django.contrib.auth.hashers import make_password
from .models import CustomUser, Role, Material, Ticket, UnidadMedida
from django import forms
from django.core.exceptions import ValidationError
from .models import CustomUser
from django import forms

class CustomUserForm(UserChangeForm):  # Cambiar a UserChangeForm si no estás creando un nuevo usuario
    email = forms.EmailField(
        required=True,
        label="Correo Electrónico",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ingresa tu correo'})
    )
    username = forms.CharField(
        required=True,
        label="Nombre de Usuario",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'})
    )
    roles = forms.ModelMultipleChoiceField(
        queryset=Role.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control select-multiple'}),
        label="Roles del Usuario",
        required=True
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,  # No requerido si no se quiere cambiar la contraseña
        label="Nueva Contraseña"
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,  # No requerido si no se quiere cambiar la contraseña
        label="Confirmar Contraseña"
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'roles', 'password1', 'password2']

# Formulario para la creación y edición de materiales
class MaterialForm(forms.ModelForm):
    unidad_medida = forms.ModelChoiceField(
        queryset=UnidadMedida.objects.all(),
        label="Unidad de Medida",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Material
        fields = ['nombre', 'descripcion', 'unidad_medida', 'cantidad_disponible', 'stock', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'cantidad_disponible': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

# Formulario para la creación de tickets
class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['material_solicitado', 'cantidad']
        widgets = {
            'material_solicitado': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control'})
        }

# Formulario para filtrar reportes por fecha y material
class ReportFilterForm(forms.Form):
    fecha_inicio = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Fecha de Inicio"
    )
    fecha_fin = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Fecha de Fin"
    )
    material = forms.ModelChoiceField(
        queryset=Material.objects.filter(activo=True),
        required=False,
        label="Material",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
