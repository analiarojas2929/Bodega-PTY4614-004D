from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views
from django.contrib.auth import views as auth_views


# Definir las rutas
urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='Modulo_usuario/usuarios/login.html'), name='login'),
    path('home', views.home_view, name='home'),
    path('admin_login/', auth_views.LoginView.as_view(template_name='Modulo_administrador/usuarios/login.html'), name='admin_login'),
    path('inventory/', views.inventory, name='inventory'),
    path('lista_view/', views.lista_view, name='lista_view'),
    path('add_material/', views.add_material_view, name='add_material'),
    path('update_material/<int:id>/', views.update_material_view, name='update_material'),
    path('delete_material/<int:id>/', views.delete_material_view, name='delete_material'),
    path('restore_material/<int:id>/', views.restore_material_view, name='restore_material'),
    path('stock_alerts/', views.stock_alerts_view, name='stock_alerts'),
    path('reports/', views.reports_view, name='reports'),
    path('crear_ticket/', views.crear_ticket, name='crear_ticket'),
    path('lista_tickets/', views.lista_tickets, name='lista_tickets'),
    path('ver_ticket/<int:ticket_id>/', views.ver_ticket, name='ver_ticket'),
    path('eliminar_ticket/<int:ticket_id>/', views.eliminar_ticket, name='eliminar_ticket'),
    path('create_user/', views.create_user, name='create_user'),
    path('restricted/', views.redirect_home_administrador, name='restricted_view'),  # Vista restringida, solo una vez
    path('login/', auth_views.LoginView.as_view(template_name='usuarios/login.html'), name='login'),
    path('accounts/', include('allauth.urls')),  # Para el login de terceros (Google, etc.)
    path('access_denied/', views.access_denied_view, name='access_denied'),  # Vista para acceso denegado
    path('logout/', views.custom_logout_view, name='logout'),

]
