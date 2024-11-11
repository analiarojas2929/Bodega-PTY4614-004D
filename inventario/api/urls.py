# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MaterialViewSet
from . import views


router = DefaultRouter()
router.register(r'materiales', MaterialViewSet, basename='material')

urlpatterns = [
    path('', include(router.urls)),
    path('sync_materiales/', views.sync_materiales, name='sync_materiales'),
]
