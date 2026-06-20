from apps.utils.ModelViewSetClass import ModelViewSetClass
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from apps.contabilidad.services.consulta_service import *

class ConsultasViewSet(viewsets.ViewSet):
    
    @action(methods=['POST'], detail=False, url_path='consulta_filtro_aux')
    def consulta_filtro_aux(self, request):
        return Response(ConsultaService.filtro_aux(request.data['model'], request.data['filtro']))