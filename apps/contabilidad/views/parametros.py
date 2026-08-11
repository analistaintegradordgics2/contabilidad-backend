from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from apps.contabilidad.models.parametros import TipoRetencion, CentroCostos
from apps.contabilidad.serializers.centrocostos import CentroCostosSerializer

class ParametrosViewSet(viewsets.ViewSet):

    @action(methods=['get'], detail=False, url_path='tipo_retencion')
    def tipo_retencion(self, request):
        query = list(TipoRetencion.objects.filter(activo=True).values(
            "id", "nombre", "porcentaje_defecto", "base_sobre", "cuenta_contable_id"
        ))
        return Response(query)


    @action(methods=['get'], detail=False, url_path='tipo_electronica')
    def tipo_electronica(self, request):
        query = [
            {"id": 1, "nombre": "Factura electrónica"},
            {"id": 2, "nombre": "Nota débito"},
            {"id": 3, "nombre": "Nota crédito"},
            {"id": 4, "nombre": "Documento soporte"},
            {"id": 5, "nombre": "Nota ajuste"},
        ]
        return Response(query)

class CentroCostosViewSet(viewsets.ModelViewSet):
    queryset = CentroCostos.objects.all().order_by('codigo')
    serializer_class = CentroCostosSerializer
    def list(self, request, *args, **kwargs):
        tipo = request.GET.get("tipo", None)
        if tipo == None :
            query = CentroCostos.objects.filter(estado=True).order_by('codigo')
        else :
            query = CentroCostos.objects.filter(estado=True, tipo=tipo).order_by('codigo')

        data = CentroCostosSerializer(query, many=True).data

        return Response(data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):

        request.data['uc'] = request.user.id
        request.data['um'] = request.user.id

        centroscostos = CentroCostosSerializer(data=request.data)

        if request.data['id'] != None:
            query_centroscostos = CentroCostos.objects.get(pk=request.data['id'])
            centroscostos = CentroCostosSerializer(query_centroscostos, data=request.data)

        centroscostos.is_valid(raise_exception=True)
        centroscostos.save()

        return Response("OK", status=status.HTTP_200_OK)