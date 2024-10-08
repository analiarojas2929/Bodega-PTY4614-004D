from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Role

class CustomUserCreationForm(UserCreationForm):
    roles = forms.ModelMultipleChoiceField(
        queryset=Role.objects.all(),
        widget=forms.CheckboxSelectMultiple,  # Permitir selección múltiple con checkboxes
        required=True
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'roles')  # Añade el campo de roles


