from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from apps.contabilidad.models.parametros import TipoRetencion

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