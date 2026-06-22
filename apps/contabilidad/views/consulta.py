from apps.utils.ModelViewSetClass import ModelViewSetClass
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from apps.contabilidad.services.consulta_service import *

class ConsultasViewSet(viewsets.ViewSet):
    
    @action(methods=['POST'], detail=False, url_path='consulta_filtro_aux')
    def consulta_filtro_aux(self, request):
        return Response(ConsultaService.filtro_aux(request.data['model'], request.data['filtro']))
    
    @action(methods=['POST'], detail=False, url_path='consulta_saldos_aux')
    def consulta_saldos_aux(self, request):
        model = request.data.get('model', {})
        return Response({
            'sumsaldos': ConsultaService.consulta_saldos_aux(model),
        }, status=status.HTTP_200_OK)
    
    @action(methods=['POST'], detail=False, url_path='imprimir_consulta_aux')
    def imprimir_consulta_aux(self, request):
        return ConsultaService.imprimir_consulta_aux(request.data)
    
    @action(methods=['GET'], detail=False, url_path='centro_costos')
    def centro_costos(self, request, *args, **kwargs):
        return ConsultaService.centro_costos()