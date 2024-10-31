# En context_processors.py
from .roles import ADMINISTRADOR_OBRA, JEFE_BODEGA, JEFE_OBRA

def role_context(request):
    user = request.user
    if user.is_authenticated:
        return {
            'can_access_ticket': user.roles.filter(id=JEFE_BODEGA).exists() or user.roles.filter(id=JEFE_OBRA).exists(),
            'can_access_inventario': user.roles.filter(id=JEFE_BODEGA).exists() or user.roles.filter(id=JEFE_OBRA).exists(),
            'can_access_reportes': user.roles.filter(id=ADMINISTRADOR_OBRA).exists(),
            'is_administrador_obra': user.roles.filter(id=ADMINISTRADOR_OBRA).exists(),
        }
    return {}
