import pdb
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction

from apps.nomina.services.cargo_service import CargoService
from apps.nomina.models.contratos import Cargo
from apps.nomina.serializers.contratos import CargoModelSerializer


class CargoViewSet(viewsets.ModelViewSet):
    queryset = Cargo.objects.all().order_by('nombre')
    serializer_class = CargoModelSerializer

    def list(self, request, *args, **kwargs):
        estado = request.GET.get("estado", "").lower() == "true"

        if estado == None :
            query = self.get_queryset()
        else :
            query = self.get_queryset().filter(estado=estado).order_by('nombre')
        
        data = self.serializer_class(query, many=True).data

        return Response(data, status=status.HTTP_200_OK)
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        data = request.data
        CargoService.crear_o_actualizar(data)

        return Response("OK", status=status.HTTP_200_OK)