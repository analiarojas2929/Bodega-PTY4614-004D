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

class CustomUserForm(UserChangeForm):
    email = forms.EmailField(
        required=True,
        label="Correo Electrónico",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ingresa el correo electrónico'})
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
        required=False,  # Contraseña opcional
        label="Nueva Contraseña"
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,  # Confirmación opcional
        label="Confirmar Contraseña"
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'roles', 'is_active']  # Incluye campos adicionales según el modelo

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        # Validar si las contraseñas coinciden (si están presentes)
        if password1 or password2:
            if password1 != password2:
                raise ValidationError("Las contraseñas no coinciden.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password1 = self.cleaned_data.get("password1")
        if password1:  # Si se proporcionó una nueva contraseña, actualízala
            user.set_password(password1)
        if commit:
            user.save()
            self.save_m2m()  # Guardar relaciones ManyToMany (roles)
        return user
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
