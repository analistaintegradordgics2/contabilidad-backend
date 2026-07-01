from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from apps.afiliados.serializers.causacion import ConceptoCausacionSerializer
from apps.afiliados.models.causacion import ConceptoCausacion, AfiliadoConceptoCausacion
from apps.afiliados.services.facturacion_service import AfiliadoFacturacionService

class AfiliadoCausacionViewSet(viewsets.ModelViewSet):
    queryset = ConceptoCausacion.objects.all()
    serializer_class = ConceptoCausacionSerializer
    pagination_class = None

    def perform_create(self, serializer):
        serializer.save(uc=self.request.user)

    def perform_update(self, serializer):
        serializer.save(um=self.request.user)


    @action(methods=['POST'], detail=False, url_path='facturar_afiliados')
    def facturar_afiliados(self, request, *args, **kwargs):
  
        data         = request.data
        afiliado_id  = data.get('afiliado_id')
        mes          = data.get('mes')
        anio         = data.get('anio')


        # Determinar qué tipos de documento (resoluciones) se van a usar
        tipos_factura_ids = list(
            AfiliadoConceptoCausacion.objects
            .filter(
                afiliado_id=afiliado_id[0]
            )
            .values_list('concepto__tipo_factura_id', flat=True)
            .distinct()
        )

        # Validar resolución/numeración disponible para cada tipo 
        # errores = AfiliadoFacturacionService.validar_resoluciones(afiliado_id)
        # if errores:
        #     return Response({'validate': errores, 'status': 400},
        #                     status=status.HTTP_400_BAD_REQUEST)

        # ─── Facturar ───
        try:
            resultado = AfiliadoFacturacionService.facturar_afiliado(
                afiliado_id[0], mes, anio, request.user.id
            )
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_404_NOT_FOUND)

        return Response({'data': resultado, 'status': 200})

      

    