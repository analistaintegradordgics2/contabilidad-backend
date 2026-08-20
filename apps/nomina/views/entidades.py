import pdb

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from apps.nomina.services.entidad_service import EntidadService
from apps.nomina.models.entidades import Entidad, TipoEntidad
from apps.nomina.serializers.entidades import EntidadSerializer, TipoEntidadSerializer

class EntidadViewSet(viewsets.ModelViewSet):
    queryset = Entidad.objects.all()
    serializer_class = EntidadSerializer

    def list(self, request, *args, **kwargs):
        estado = request.GET.get("estado", "").lower() == "true"

        if estado is None:
            query = self.get_queryset()
        else:
            query = self.get_queryset().filter(estado=estado)

        data = self.serializer_class(query, many=True).data
        return Response(data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        EntidadService.crear_o_actualizar(serializer.validated_data, request.user)
        return Response("OK", status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        instancia = self.get_object()
        serializer = self.serializer_class(instancia, data=request.data)
        serializer.is_valid(raise_exception=True)
        EntidadService.crear_o_actualizar(
            serializer.validated_data, request.user, instancia=serializer.instance
        )
        return Response("OK", status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False, url_path='exportar')
    def exportar(self, request, *args, **kwargs):
        return EntidadService.exportar(request.data)

    @action(methods=['POST'], detail=False, url_path='imprimir')
    def imprimir(self, request, *args, **kwargs):
        return EntidadService.imprimir(request.data)

    @action(methods=['GET'], detail=False, url_path='filtrar')
    def filtrar(self, request, *args, **kwargs):
        tipo_entidad = request.GET.get("tipo_entidad", "")
        centro_costo = request.GET.get("centro_costo", "")
        if tipo_entidad:
            query = self.get_queryset().filter(tipo_entidad=tipo_entidad)
        elif centro_costo:
            query = self.get_queryset().filter(centro_costo=centro_costo)
        else:
            query = self.get_queryset()

        data = self.serializer_class(query, many=True).data
        return Response(data, status=status.HTTP_200_OK)

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