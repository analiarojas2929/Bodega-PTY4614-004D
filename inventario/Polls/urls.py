from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('inventory/', views.inventory_view, name='inventory'),
    path('lista_view/', views.lista_view, name='lista_view'),
    path('add_material/', views.add_material_view, name='add_material'),
    path('update_material/<int:id>/', views.update_material_view, name='update_material'),
    path('delete_material/<int:id>/', views.delete_material_view, name='delete_material'),
    path('stock_alerts/', views.stock_alerts_view, name='stock_alerts'),
    path('profile/', views.profile_view, name='profile'),
    path('reports/', views.reports_view, name='reports'),
    path('settings/', views.settings_view, name='settings'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('filters/', views.filters_view, name='filters'),
    path('crear_ticket/', views.crear_ticket, name='crear_ticket'),
    path('lista_tickets/', views.lista_tickets, name='lista_tickets'),
    path('ver_ticket/<int:ticket_id>/', views.ver_ticket, name='ver_ticket'),
    path('eliminar_ticket/<int:ticket_id>/', views.eliminar_ticket, name='eliminar_ticket'),
]
