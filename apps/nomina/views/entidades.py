import pdb
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status

from django.db import transaction

from apps.nomina.services.entidad_service import EntidadService
from apps.nomina.models.entidades import Entidad, TipoEntidad, EntidadCentroCosto
from apps.nomina.serializers.entidades import EntidadSerializer, TipoEntidadSerializer, EntidadCentroCostoSerializer
from apps.personas.services.persona_service import PersonaService


class EntidadViewSet(viewsets.ModelViewSet):
    queryset = Entidad.objects.all()
    serializer_class = EntidadSerializer

    def list(self, request, *args, **kwargs):

        estado = request.GET.get("estado", "").lower() == "true"

        if estado == None :
            query = self.get_queryset()
        else :
            query = self.get_queryset().filter(estado=estado)
        
        data = self.serializer_class(query, many=True).data

        return Response(data, status=status.HTTP_200_OK)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        data = request.data
        EntidadService.crear_o_actualizar(data, request.user.id)
        return Response("OK", status=status.HTTP_200_OK)

class TipoEntidadViewSet(viewsets.ModelViewSet):

    queryset = TipoEntidad.objects.all().order_by('nombre')
    serializer_class = TipoEntidadSerializer

    def list(self, request, *args, **kwargs):
        estado = request.GET.get("estado", "").lower() == "true"

        if estado == None :
            query = self.get_queryset()
        else :
            query = self.get_queryset().filter(estado=estado)
        
        data = self.serializer_class(query, many=True).data

        return Response(data, status=status.HTTP_200_OK)