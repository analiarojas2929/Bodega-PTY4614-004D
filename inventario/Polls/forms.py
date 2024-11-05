from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Role

class CustomUserCreationForm(UserCreationForm):
    roles = forms.ModelChoiceField(
        queryset=Role.objects.all(),
        widget=forms.Select,
        required=True,
        label="Selecciona un rol",
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'roles']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Ya existe una cuenta con este correo.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()  # Guardar el usuario primero para que tengamos una instancia válida
            user.roles.set([self.cleaned_data['roles']])  # Asignar el rol seleccionado
        return user
