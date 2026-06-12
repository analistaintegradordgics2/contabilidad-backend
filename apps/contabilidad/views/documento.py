from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from apps.contabilidad.models.documento import Documentos, Mov
from apps.contabilidad.serializers.documento import *
from apps.contabilidad.services.documento_service import *
import pdb

class DocumentoViewSet(ModelViewSet):

    queryset = Documentos.objects.all().order_by('-id')
    serializer_class = DocumentoSerializer

    def create(self, request):
        try:

            documento = DocumentoService.crear(
                request.data,
                request.user.id
            )
            return Response(
                documento,
                status=status.HTTP_201_CREATED
            )

        except Exception as e:

            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'], url_path='buscar/(?P<id>[^/.]+)')
    def buscar(self, request, id= None):

        iddocumento = id

        documento = Documentos.objects.filter(
            id=iddocumento
        ).first()

        if not documento:
            return Response(
                {'error': 'Documento no encontrado'},
                status=404
            )

        return Response(
            DocumentoDetailSerializer(documento).data
        )

    @action(methods=['get'], detail=True)
    def bitacora(self, request, pk=None):
        bita = DocumentosBita.objects.filter(documentos_id=pk)
        return Response(DocumentosBitaSerializer(bita, many=True).data)