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
        })
    
    @action(methods=['POST'], detail=False, url_path='imprimir_consulta_aux')
    def imprimir_consulta_aux(self, request):
        return ConsultaService.imprimir_consulta_aux(request.data)
    
    @action(methods=['GET'], detail=False, url_path='centro_costos')
    def centro_costos(self, request, *args, **kwargs):
        return ConsultaService.centro_costos()
    
    @action(detail=False, methods=['POST'], url_path='exportar_consulta_filtro_aux')
    def exportar_consulta_filtro_aux(self, request, *args, **kwargs):
        return ConsultaService.exportar_consulta_filtro_aux(request.data)
    
    @action(detail=False, methods=['POST'], url_path='consulta_filtro_aux_banco')
    def consulta_filtro_aux_banco(self, request, *args, **kwargs):
        return Response(ConsultaService.filtro_aux_banco(request.data.get('model', {})))
    
    @action(methods=['POST'], detail=False, url_path='consulta_saldos_aux_banco')
    def consulta_saldos_aux_banco(self, request):
        model = request.data.get('model', {})
        return Response({
            'sumsaldos': ConsultaService.consulta_saldos_aux_banco(model),
        })
    
    @action(detail=False, methods=['POST'], url_path='exportar_consulta_filtro_aux_banco')
    def exportar_consulta_filtro_aux_banco(self, request, *args, **kwargs):
        return ConsultaService.exportar_consulta_filtro_aux_banco(request.data)
    
    @action(methods=['POST'], detail=False, url_path='imprimir_consulta_aux_banco')
    def imprimir_consulta_aux_banco(self, request):
        return ConsultaService.imprimir_consulta_aux_banco(request.data)
