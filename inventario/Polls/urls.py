from django.urls import include, path
from . import views
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('', views.home_view, name='home'),
    path('inventory/', views.inventory_view, name='inventory'),
    path('add_material/', views.add_material_view, name='add_material'),
    path('update_material/', views.update_material_view, name='update_material'),
    path('delete_material/', views.delete_material_view, name='delete_material'),
    path('profile/', views.profile_view, name='profile'),
    path('reports/', views.reports_view, name='reports'),
    path('settings/', views.settings_view, name='settings'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('filters/', views.filters_view, name='filters'),
]

