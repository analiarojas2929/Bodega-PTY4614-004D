# inventory/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MaterialViewSet

# Configura el enrutador y registra el viewset de Material
router = DefaultRouter()
router.register(r'materials', MaterialViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
