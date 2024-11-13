# En context_processors.py
from .roles import ADMINISTRADOR_OBRA, JEFE_BODEGA, JEFE_OBRA, CAPATAZ, ADMINISTRADOR_SISTEMA

def get_role_context(request):
    user = request.user
    if user.is_authenticated:
        return {
            'is_jefe_bodega': user.roles.filter(id=JEFE_BODEGA).exists(),
            'is_jefe_obra': user.roles.filter(id=JEFE_OBRA).exists(),
            'is_capataz': user.roles.filter(id=CAPATAZ).exists(),
            'can_access_ticket': user.roles.filter(id=CAPATAZ).exists() or user.roles.filter(id=JEFE_OBRA).exists(),
            'can_access_inventario': user.roles.filter(id=JEFE_BODEGA).exists() or user.roles.filter(id=JEFE_OBRA).exists(),
            'can_access_reportes': user.roles.filter(id=ADMINISTRADOR_OBRA).exists(),
            'is_administrador_obra': user.roles.filter(id=ADMINISTRADOR_OBRA).exists(),
            'is_administrador_sistema': user.roles.filter(id=ADMINISTRADOR_SISTEMA).exists(),
            'can_access_list_ticket': user.roles.filter(id=JEFE_BODEGA).exists(),
            'can_access_actions': user.roles.filter(id=ADMINISTRADOR_OBRA).exists() or user.roles.filter(id=CAPATAZ).exists(),
        }
    return {}
