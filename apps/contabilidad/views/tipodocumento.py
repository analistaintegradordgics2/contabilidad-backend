# apps/contabilidad/views/tipodocumento.py

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q

from apps.utils.ModelViewSetClass import ModelViewSetClass
from apps.contabilidad.models.tipodocumento import TiposDocumentos, Fuentes, FormaPagoElectro, MedioPagoElectro, FacturacionElectronica
from apps.contabilidad.serializers.tipodocumento import (
    TiposDocumentosSerializer,
    TiposDocumentosListSerializer,
    TiposDocumentosHistorySerializer,
    FuentesSerializer,
    FormaPagoElectroSerializer,FacturacionElectronicaSelectSerializer, MedioPagoElectroSerializer
)
from apps.contabilidad.services.tipodocumento_service import TipoDocumentoService
# from apps.contabilidad.selectors.tipodocumento_selectors import (
#     get_tipos_documento,
#     format_tipo_documento_select
# )


class TiposDocumentosViewSet(ModelViewSetClass):
    queryset         = TiposDocumentos.objects.all().order_by('nombre')
    serializer_class = TiposDocumentosListSerializer

    def list(self, request, *args, **kwargs):

        queryset = TiposDocumentos.objects.filter(estado=True)
        return Response(
            TiposDocumentosListSerializer(queryset, many=True).data,
            status=status.HTTP_200_OK
        )

    def create(self, request, *args, **kwargs):
        tipo_id = request.data.get('id')
        tipo    = TipoDocumentoService.crear_o_actualizar(request.data, tipo_id)
        return Response(
            TiposDocumentosSerializer(tipo).data,
            status=status.HTTP_201_CREATED
        )

    @action(methods=['post'], detail=False, url_path='selectnew')
    def selectnew(self, request):
        tipo_id = request.data.get('id')
        search  = request.data.get('search', '')
        tipo    = request.data.get('tipo', None)    # I, E, N, F

        if tipo_id:
            item = TiposDocumentos.objects.filter(pk=tipo_id).first()
            return Response([format_tipo_documento_select(item)])

        queryset = get_tipos_documento(tipo=tipo, search=search)[:10]
        return Response([format_tipo_documento_select(i) for i in queryset])


    @action(methods=['get'], detail=False, url_path='por-tipo/(?P<tipo>[^/.]+)')
    def por_tipo(self, request, tipo=None):
        queryset = get_tipos_documento(tipo=tipo)
        return Response(
            TiposDocumentosListSerializer(queryset, many=True).data,
            status=status.HTTP_200_OK
        )

    @action(methods=['get'], detail=False, url_path='fuentes')
    def fuentes(self, request):
        fuentes = Fuentes.objects.all().order_by('nombre')
        return Response(FuentesSerializer(fuentes, many=True).data)

    @action(methods=['get'], detail=False, url_path='configuraciones-fe')
    def configuraciones_fe(self, request):
        estado = request.GET.get('estado', None)
        if estado is not None:
            estado = estado == 'true'
        
        queryset = FacturacionElectronica.objects.all()
        if estado is not None:
            queryset = queryset.filter(estado=estado)


        return Response(
            FacturacionElectronicaSelectSerializer(
                queryset,
                many=True
            ).data
        )

    # ─────────────────────────────────────
    # Formas de pago
    # ─────────────────────────────────────
    @action(methods=['get'], detail=False, url_path='formas_pago')
    def formas_pago(self, request):
        forma_pago = FormaPagoElectro.objects.all().order_by('nombre')
        return Response(
            FormaPagoElectroSerializer(forma_pago, many=True).data
        )

    # ─────────────────────────────────────
    # Medios de pago
    # ─────────────────────────────────────
    @action(methods=['get'], detail=False, url_path='medios_pago')
    def medios_pago(self, request):
        medio_pago = MedioPagoElectro.objects.all().order_by('nombre')
        return Response(
            MedioPagoElectroSerializer(medio_pago, many=True).data
        )
    
    @action(methods=['get'], detail=False, url_path='history/(?P<id>[^/.]+)')
    def history(self, request, id=None):
        query = TiposDocumentos.objects.filter(pk=id).first()
        return Response(
            TiposDocumentosHistorySerializer(query).data,
            status=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        tipo_id       = kwargs.get('pk')
        puede, mensaje = TipoDocumentoService.puede_eliminar(tipo_id)

        if not puede:
            return Response(
                {'error': mensaje},
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().destroy(request, *args, **kwargs)