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