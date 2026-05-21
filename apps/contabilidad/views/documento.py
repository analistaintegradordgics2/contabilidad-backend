from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from apps.contabilidad.models.documento import Documentos, Mov
from apps.contabilidad.serializers.documento import *
from apps.contabilidad.services.documento_service import *

class DocumentoViewSet(ModelViewSet):

    queryset = Documentos.objects.all().order_by('-id')
    serializer_class = DocumentoSerializer

    def create(self, request, *args, **kwargs):

        documento = DocumentoService.crear(
            request.data,
            request.user
        )

        return Response(
            DocumentoSerializer(documento).data,
            status=status.HTTP_201_CREATED
        )

    @action(methods=['get'], detail=True)
    def bitacora(self, request, pk=None):
        bita = DocumentosBita.objects.filter(documentos_id=pk)
        return Response(DocumentosBitaSerializer(bita, many=True).data)