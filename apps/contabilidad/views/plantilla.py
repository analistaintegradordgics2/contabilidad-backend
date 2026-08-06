import logging
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from apps.contabilidad.models.plantilla import PlantillaDocumento
from apps.contabilidad.serializers.plantilla import PlantillaDocumentoSerializer
from apps.contabilidad.services.plantilla_service import PlantillaService

logger = logging.getLogger(__name__)


class PlantillaDocumentoViewSet(ModelViewSet):
    """
    ViewSet para la parametrización (Contador) y ejecución (Auxiliar) de plantillas de comprobantes automáticos.
    """
    queryset = PlantillaDocumento.objects.filter(activa=True).order_by('nombre')
    serializer_class = PlantillaDocumentoSerializer
    pagination_class = None

    def get_queryset(self):
        # Si la solicitud es para administración (Contador), se pueden listar todas (activas e inactivas)
        if self.request.query_params.get('todas') == 'true':
            return PlantillaDocumento.objects.all().order_by('nombre')
        return PlantillaDocumento.objects.filter(activa=True).order_by('nombre')

    def create(self, request, *args, **kwargs):
        try:
            plantilla = PlantillaService.guardar_plantilla(request.data)
            serializer = self.get_serializer(plantilla)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error en create PlantillaDocumentoViewSet: {str(e)}", exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            pk = kwargs.get('pk')
            data = request.data.copy()
            data['id'] = pk
            plantilla = PlantillaService.guardar_plantilla(data)
            serializer = self.get_serializer(plantilla)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error en update PlantillaDocumentoViewSet: {str(e)}", exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['POST'], url_path='ejecutar')
    def ejecutar(self, request, pk=None):
        """
        Endpoint invocado por el Auxiliar para generar el documento contable a partir de la plantilla.
        """
        try:
            resultado = PlantillaService.ejecutar(
                plantilla_id=pk,
                datos=request.data,
                usuario_id=request.user.id
            )
            return Response(resultado, status=status.HTTP_201_CREATED)
        except ValueError as ve:
            return Response({'error': str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error en endpoint ejecutar plantilla {pk}: {str(e)}", exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['POST'], url_path='preview')
    def preview(self, request, pk=None):
        """
        Endpoint para calcular la simulación de débitos y créditos antes de guardar.
        """
        try:
            valor = request.data.get('valor', 0)
            simulacion = PlantillaService.preview(plantilla_id=pk, valor=valor)
            return Response(simulacion, status=status.HTTP_200_OK)
        except ValueError as ve:
            return Response({'error': str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error en endpoint preview plantilla {pk}: {str(e)}", exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['POST'], url_path='duplicar')
    def duplicar(self, request, pk=None):
        """
        Endpoint para clonar una plantilla existente con todas sus líneas de asiento.
        """
        try:
            nueva = PlantillaService.duplicar_plantilla(pk)
            serializer = self.get_serializer(nueva)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error duplicando plantilla {pk}: {str(e)}", exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
