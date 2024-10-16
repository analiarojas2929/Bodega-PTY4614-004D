from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Role, Material, UnidadMedida, EstadoTicket, Ticket, Proveedor, EstadoPedido, Pedido, TipoReporte, Reporte

# Registrar modelos que no requieren personalización en el admin
admin.site.register(Material)
admin.site.register(UnidadMedida)
admin.site.register(EstadoTicket)
admin.site.register(Ticket)
admin.site.register(Proveedor)
admin.site.register(EstadoPedido)
admin.site.register(Pedido)
admin.site.register(TipoReporte)
admin.site.register(Reporte)
admin.site.register(Role)

# Registrar el modelo CustomUser con el campo `roles`
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'get_roles', 'is_staff', 'is_active')  # Usamos 'get_roles' para mostrar roles
    
    # Método para mostrar los roles asociados al usuario
    def get_roles(self, obj):
        return ", ".join([role.name for role in obj.roles.all()])

    get_roles.short_description = 'Roles'  # Nombre de la columna en el admin

    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('roles',)}),  # Mostrar los roles en la vista de edición de usuario
    )

# Registrar el modelo CustomUser en el admin
admin.site.register(CustomUser, CustomUserAdmin)
