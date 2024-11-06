from django.shortcuts import render
from rest_framework import viewsets
from .models import Material
from .serializers import MaterialSerializer
from rest_framework.response import Response
from rest_framework import status

# Create your views here.
class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer

    def destroy(self, request, *args, **kwargs):
        material = self.get_object()
        material.activo = False
        material.save()
        return Response(status=status.HTTP_204_NO_CONTENT)