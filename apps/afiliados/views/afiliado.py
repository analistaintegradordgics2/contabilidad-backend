from apps.afiliados.serializers.afiliado import *
from apps.personas.models.persona import Persona
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from apps.afiliados.services.afiliado_service import AfiliadoService
from apps.afiliados.models.afiliado import Afiliado
from rest_framework.decorators import action
from apps.afiliados.serializers.facturacion import FacturacionAfiliadosSerializer
from apps.utils.history import getCombinedHistory
from apps.afiliados.models.causacion import AfiliadoConceptoCausacion

class AfiliadoViewSet(viewsets.ModelViewSet):
    queryset = Afiliado.objects.filter(activo=True)
    serializer_class = AfiliadoModelSerializer
    pagination_class = None

    def get_serializer_class(self):
        if not self.request.GET.get('sin_facturar'):
            return AfiliadoModelSerializer

        sin_facturar = (
            self.request.GET.get('sin_facturar', '').lower() == 'true'
        )

        if sin_facturar:
            return AfiliadoModelSerializer

        return FacturacionAfiliadosSerializer

    def list(self, request, *args, **kwargs):
        sin_facturar = request.GET.get('sin_facturar', '').lower() == 'true'
        
        service = AfiliadoService()
        afiliados = service.afiliados_facturacion(request.GET, sin_facturar)
        
        serializer = self.get_serializer(afiliados, many=True, context={'conceptos_facturar': True})
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            service = AfiliadoService(request.user)
            try:
                afiliado = service.create_afiliado(serializer.validated_data)
            except Exception as e:
                return Response({'msg': f"Error inesperado: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
            return Response(self.get_serializer(afiliado).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        # pdb.set_trace()
        # request.data['aplicativo'] = request.data['aplicativo']['id']
        # request.data['persona'] = request.data['persona']['id']
        # request.data['tipo_contrato'] = request.data['tipo_contrato']['id']
        partial = kwargs.pop('partial', False)
        afiliado = Afiliado.objects.get(pk=kwargs['pk'])
        serializer = self.get_serializer(afiliado, data=request.data, partial=partial)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        service = AfiliadoService(request.user)
        try:
            afiliado = service.update_afiliado(kwargs['pk'], data=serializer.validated_data)
        except Afiliado.DoesNotExist:
            return Response({'msg': 'Afiliado no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        return Response(self.get_serializer(afiliado).data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='personas')
    def personas(self, request, *args, **kwargs):
        queryset = Persona.objects.filter(personas_tipos_personas_persona__tipo_persona__nombre__iexact='Afiliado')
        serializer = AfiliadoListSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False, url_path='history/(?P<id>[^/.]+)')
    def history(self, request, id=None):
       
        afiliado = Afiliado.objects.filter(pk=id).first()
        if not afiliado:
            return Response({'history': []}, status=status.HTTP_200_OK)

        campos_afiliado = [
            {'db': 'nombre',           'label': 'Nombre'},
            {'db': 'tipo_contrato_id', 'label': 'Tipo Contrato', 'nombre_relacion': 'nombre'},
            {'db': 'aplicativo_id',    'label': 'Aplicativo', 'nombre_relacion': 'nombre'},
            {'db': 'fecha_inicio',     'label': 'Fecha Inicio'},
            {'db': 'fecha_fin',        'label': 'Fecha Fin'},
            {'db': 'porc_reajuste',    'label': '% Reajuste'},
            {'db': 'fecha_reajuste',   'label': 'Fecha Reajuste'},
            {'db': 'activo',           'label': 'Estado'},
            {'db': 'history_date',     'label': 'fecha_bitacora'},
            {'db': 'history_user_id',  'label': 'usuario_bitacora', 'nombre_relacion': 'username'},
        ]

        related_models = [
            {
                'history_manager': AfiliadoConceptoCausacion.history,
                'fk_field': 'afiliado_id',
                'tipo': 'Concepto de Causación',
                'campos': [
                    {'db': 'concepto_id', 'label': 'Concepto', 'nombre_relacion': 'nombre'},
                    {'db': 'valor',       'label': 'Valor'},
                    {'db': 'detalle',     'label': 'Detalle'},
                    {'db': 'porcentaje',  'label': 'Porcentaje'},
                    {'db': 'facturar',    'label': 'Facturar'},
                ]
            }
        ]

        history_data = getCombinedHistory(
            obj=afiliado,
            campos_principal=campos_afiliado,
            tipo='Afiliación',
            related_models=related_models
        )

        return Response({'history': history_data}, status=status.HTTP_200_OK)

