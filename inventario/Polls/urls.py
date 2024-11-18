from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views
from django.contrib.auth import views as auth_views
from .views import QuestionViewSet, ChoiceViewSet

from api.views import buscar_material_ajax
from . import views
router = DefaultRouter()
router.register(r'questions', QuestionViewSet, basename='question')
router.register(r'choices', ChoiceViewSet, basename='choice')


# Definir las rutas
urlpatterns = [
    path('', views.user_login, name='login'),
    path('home', views.home_view, name='home'),
    path('inventory/', views.inventory, name='inventory'),
    path('lista_view/', views.lista_view, name='lista_view'),
    path('add_material/', views.add_material_view, name='add_material'),
    path('delete_material/<int:id>/', views.delete_material_view, name='delete_material'),
    path('restore_material/<int:id>/', views.restore_material_view, name='restore_material'),
    path('stock_alerts/', views.stock_alerts_view, name='stock_alerts'),
    path('reports/', views.reports_view, name='reports_view'),
    path('tickets/', views.lista_tickets, name='lista_tickets'),
    path('crear_ticket/', views.crear_ticket, name='crear_ticket'),
    path('cobrar_ticket/<int:ticket_id>/', views.cobrar_ticket, name='cobrar_ticket'),
    path('ver_ticket/<int:ticket_id>/', views.ver_ticket, name='ver_ticket'),
    path('eliminar_ticket/<int:ticket_id>/', views.eliminar_ticket, name='eliminar_ticket'),
    path('create_user/', views.create_user, name='create_user'),
    path('restricted/', views.redirect_home_administrador, name='restricted_view'),  # Vista restringida, solo una vez
    path('accounts/', include('allauth.urls')),  # Para el login de terceros (Google, etc.)
    path('access_denied/', views.access_denied_view, name='access_denied'),  # Vista para acceso denegado
    path('logout/', views.logout_view, name='logout'),
    path('admin-user-list/', views.admin_user_list, name='admin_user_list'),
    path('home_admin/', views.home_admin, name='home_admin'),
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('usuarios/inactivar/<int:user_id>/', views.inactivar_usuario, name='inactivar_usuario'),
    path('usuarios/editar/<int:user_id>/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/crear/', views.crear_usuario, name='crear_usuario'),
    path('editar_material/<int:material_id>/', views.editar_material, name='editar_material'),
    path('buscar_material_ajax/', buscar_material_ajax, name='buscar_material_ajax'),
    path('usuarios/activar/<int:user_id>/', views.activar_usuario, name='activar_usuario'),  # Nueva URL para activar
    path('export_to_pdf/', views.export_to_pdf, name='export_to_pdf'),
    path('export_to_excel/', views.export_to_excel, name='export_to_excel'),
    path('movimientos/', views.movimientos_view, name='movimientos'),
    
]
