from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Role

admin.site.register(Material)
admin.site.register(UnidadMedida)
admin.site.register(EstadoTicket)
admin.site.register(Ticket)
admin.site.register(Proveedor)
admin.site.register(EstadoPedido)
admin.site.register(Pedido)
admin.site.register(TipoReporte)
admin.site.register(Reporte)


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('roles',)}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Role)
