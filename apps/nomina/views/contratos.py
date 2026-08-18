import pdb, json

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from django.db import transaction

from apps.nomina.services.cargo_service import CargoService
from apps.nomina.services.contrato_service import ContratoNominaService
from apps.nomina.models.contratos import Cargo, ContratoNomina, ContratoNominaNovedades
from apps.nomina.serializers.contratos import CargoModelSerializer, ContratoNominaCreateSerializer, ContratoNominaArchivoSerializer, ContratoNominaListSerializer, ContratoNominaSerializer, ContratoNominaNovedadesSerializer, ContratoNominaNovedadesListCreateSerializer, ContratoNovedadesPeriodosCreateSerializer
from apps.nomina.models.parametrizacion import TipoContrato, TipoTrabajador, NivelRiesgo
from apps.nomina.serializers.parametrizacion import TipoContratoSerializer, TipoTrabajadorSerializer, NivelRiesgoSerializer


class CargoViewSet(viewsets.ModelViewSet):
    queryset = Cargo.objects.all().order_by('nombre')
    serializer_class = CargoModelSerializer

    def list(self, request, *args, **kwargs):
        estado = request.GET.get("estado", "").lower() == "true"

        if estado is None:
            query = self.get_queryset()
        else:
            query = self.get_queryset().filter(estado=estado).order_by('nombre')

        data = self.serializer_class(query, many=True).data
        return Response(data, status=status.HTTP_200_OK)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        CargoService.crear_o_actualizar(serializer.validated_data, user=request.user)
        return Response("OK", status=status.HTTP_200_OK)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        instancia = self.get_object()
        serializer = self.serializer_class(instancia, data=request.data)
        serializer.is_valid(raise_exception=True)
        CargoService.crear_o_actualizar(
            serializer.validated_data, user=request.user, instancia=serializer.instance
        )
        return Response("OK", status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False, url_path='imprimir')
    def imprimir(self, request, *args, **kwargs):
        data = self.serializer_class(self.get_queryset(), many=True).data
        return CargoService.imprimir(data)

class TipoContratoViewSet(viewsets.ModelViewSet):

    queryset = TipoContrato.objects.all()
    serializer_class = TipoContratoSerializer

    def list(self, request, *args, **kwargs):
        estado = request.GET.get("estado", "").lower() == "true"

        if estado is None:
            query = self.get_queryset()
        else:
            query = self.get_queryset().filter(estado=estado).order_by('nombre')

        data = self.serializer_class(query, many=True).data
        return Response(data, status=status.HTTP_200_OK)

class TipoTrabajadorViewSet(viewsets.ModelViewSet):

    queryset = TipoTrabajador.objects.all()
    serializer_class = TipoTrabajadorSerializer

    def list(self, request, *args, **kwargs):
        estado = request.GET.get("estado", "").lower() == "true"

        if estado is None:
            query = self.get_queryset()
        else:
            query = self.get_queryset().filter(estado=estado).order_by('nombre')

        data = self.serializer_class(query, many=True).data
        return Response(data, status=status.HTTP_200_OK)

class NivelRiesgoViewSet(viewsets.ModelViewSet):

    queryset = NivelRiesgo.objects.all()
    serializer_class = NivelRiesgoSerializer

    def list(self, request, *args, **kwargs):
        estado = request.GET.get("estado", "").lower() == "true"

        if estado is None:
            query = self.get_queryset()
        else:
            query = self.get_queryset().filter(estado=estado).order_by('nombre')

        data = self.serializer_class(query, many=True).data
        return Response(data, status=status.HTTP_200_OK)

class ContratoNominaViewSet(viewsets.ModelViewSet):
    queryset = ContratoNomina.objects.all()
    serializer_class = ContratoNominaSerializer

    def list(self, request, *args, **kwargs):
        filtros = request.GET.get("filtros", None)
        if filtros != None :
            filtros = json.loads(filtros)
            query = self.get_queryset().filter(**filtros).order_by("persona__n_completo")
        else :
            query = self.get_queryset()
        
        data = ContratoNominaListSerializer(query, many=True).data

        return Response(data, status=status.HTTP_200_OK)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = ContratoNominaCreateSerializer(data=request.data)
        # pdb.set_trace()
        serializer.is_valid(raise_exception=True)
        resp = ContratoNominaService.crear_o_actualizar(
            serializer.validated_data, request.user
        )
        data = {
            "id": resp.id,
            "text": "OK"
        }
        return Response(data, status=status.HTTP_200_OK)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        instancia = self.get_object()
        serializer = ContratoNominaCreateSerializer(instancia, data=request.data)
        serializer.is_valid(raise_exception=True)
        resp = ContratoNominaService.crear_o_actualizar(
            serializer.validated_data, request.user, instancia=serializer.instance
        )
        data = {
            "id": resp.id,
            "text": "OK"
        }
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path='upload/(?P<contrato_id>[^/.]+)')
    def uploadContratoNomina(self, request, contrato_id=None, *args, **kwargs):
        for k, v in request.data.items():
            serializer = ContratoNominaArchivoSerializer(data={"src": v})
            serializer.is_valid(raise_exception=True)
            serializer.save(contrato_id=contrato_id, uc=request.user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=['POST'], detail=False, url_path='exportar')
    def exportar(self, request, *args, **kwargs):
        return ContratoNominaService.exportar(request.data)

    @action(detail=False, methods=['POST'], url_path='imprimir')
    def imprimir(self, request, *args, **kwargs):
        return ContratoNominaService.imprimir(request.data)

    @action(detail=True, methods=['POST'], url_path='novedades')
    def novedades(self, request, *args, **kwargs):
        data = [{**x, 'contrato': self.kwargs['pk']} for x in request.data.copy()]
        serializer = ContratoNominaNovedadesListCreateSerializer(data={'novedades': data})
        serializer.is_valid(raise_exception=True)
        ContratoNominaService.crear_o_actualizar_novedades(
            serializer.validated_data['novedades'], request.user, kwargs['pk']
        )
        return Response(
            ContratoNominaNovedadesSerializer(ContratoNominaNovedades.objects.filter(contrato_id=kwargs['pk']), many=True).data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['POST'], url_path='novedades_periodos')
    def novedades_periodos(self, request, *args, **kwargs):
        serializer = ContratoNovedadesPeriodosCreateSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        ContratoNominaService.crear_o_actualizar_novedades_periodos(serializer.validated_data, user=request.user)

        return Response("OK", status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['GET'], url_path='listar_novedades')
    def listar_novedades(self, request, *args, **kwargs):
        data = ContratoNominaService.listar_novedades(kwargs['pk'])
        serialized_data = ContratoNominaNovedadesSerializer(data, many=True)
        return Response(serialized_data.data, status=status.HTTP_200_OK)