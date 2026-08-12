import pdb, json
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from django.db import transaction
from django.db.models import Q

from apps.nomina.services.novedad_service import NovedadService
from apps.nomina.models.novedades import TipoNovedad, TipoValorNovedad, GrupoNomina, Novedad
from apps.nomina.serializers.novedades import TipoNovedadSerializer, TipoValorNovedadSerializer, GrupoNominaSerializer, NovedadSerializer, NovedadCreateSerializer, HistoryNovedadesSerializer


class TipoNovedadViewSet(viewsets.ModelViewSet):
    queryset = TipoNovedad.objects.all()
    serializer_class = TipoNovedadSerializer

    def list(self, request, *args, **kwargs):

        estado = request.GET.get("estado", "").lower() == "true"

        if estado == None :
            query = self.get_queryset()
        else :
            query = self.get_queryset().filter(estado=estado)
        
        data = self.serializer_class(query, many=True).data

        return Response(data, status=status.HTTP_200_OK)

class TipoValorNovedadViewSet(viewsets.ModelViewSet):

    queryset = TipoValorNovedad.objects.all()
    serializer_class = TipoValorNovedadSerializer

    def list(self, request, *args, **kwargs):

        estado = request.GET.get("estado", "").lower() == "true"

        if estado == None :
            query = self.get_queryset()
        else :
            query = self.get_queryset().filter(estado=estado)
        
        data = self.serializer_class(query, many=True).data

        return Response(data, status=status.HTTP_200_OK)

class GrupoNominaViewSet(viewsets.ModelViewSet):

    queryset = GrupoNomina.objects.all()
    serializer_class = GrupoNominaSerializer

    def list(self, request, *args, **kwargs):

        estado = request.GET.get("estado", "").lower() == "true"

        if estado == None :
            query = self.get_queryset()
        else :
            query = self.get_queryset().filter(estado=estado)
        
        data = self.serializer_class(query, many=True).data

        return Response(data, status=status.HTTP_200_OK)

class NovedadViewSet(viewsets.ModelViewSet):

    queryset = Novedad.objects.all().order_by("nombre")
    serializer_class = NovedadSerializer

    def list(self, request, *args, **kwargs):
        estado = request.GET.get("estado", "").lower() == "true"
        filtros = request.GET.get("filtros", None)

        if filtros is not None:
            filtros = json.loads(filtros)
            if estado is not None:
                filtros["estado"] = estado
            try:
                centro_costos = filtros["centro_costos"]
                filtros.pop("centro_costos")
                query = self.get_queryset().filter(**filtros)
                query = query.filter(
                    Q(novedades_centro_costos_novedades__centro_costos=centro_costos) |
                    Q(novedades_centro_costos_novedades__entidades_centro_costos__centro_costos_id=centro_costos),
                    novedades_centro_costos_novedades__eliminado=False
                )
                filtros["centro_costos"] = centro_costos
                data = NovedadSerializer(query, many=True, context={"filtros": filtros}).data
            except:
                query = self.get_queryset().filter(**filtros)
                data = NovedadSerializer(query, many=True).data
        else:
            if estado is None:
                query = self.get_queryset()
            else:
                query = self.get_queryset().filter(estado=estado)
            data = NovedadSerializer(query, many=True).data

        return Response(data, status=status.HTTP_200_OK)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = NovedadCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        NovedadService.crear_o_actualizar(serializer.validated_data, request.user.id)
        return Response("OK", status=status.HTTP_200_OK)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        instancia = self.get_object()
        serializer = NovedadCreateSerializer(instancia, data=request.data)
        serializer.is_valid(raise_exception=True)
        NovedadService.crear_o_actualizar(
            serializer.validated_data, request.user.id, instancia=serializer.instance
        )
        return Response("OK", status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path='history')
    def HistoryNovedades(self, request, *args, **kwargs):
        instancia = self.get_object()
        return Response(HistoryNovedadesSerializer(instancia).data, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False, url_path='exportar')
    def exportar(self, request, *args, **kwargs):
        return NovedadService.exportar(request.data)

    @action(methods=['POST'], detail=False, url_path='imprimir')
    def imprimir(self, request, *args, **kwargs):
        return NovedadService.imprimir(request.data)