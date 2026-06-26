from apps.utils.ModelViewSetClass import ModelViewSetClass
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from apps.contabilidad.services.consultas.auxiliar_service import ConsultaService
from apps.contabilidad.services.consultas.informe_service import InformeService
from rest_framework import status
from apps.utils.util import NumeroA

class ConsultasViewSet(viewsets.ViewSet):
    
    @action(methods=['POST'], detail=False, url_path='consulta_filtro_aux')
    def consulta_filtro_aux(self, request):
        try:
            return Response(ConsultaService.filtro_aux(request.data['model'], request.data['filtro']))
        except Exception:
            return Response("Error en el proceso por favor revisar.", status=status.HTTP_404_NOT_FOUND)

    @action(methods=['POST'], detail=False, url_path='consulta_saldos_aux')
    def consulta_saldos_aux(self, request):
        model = request.data.get('model', {})
        return Response({
            'sumsaldos': ConsultaService.consulta_saldos_aux(model),
        })
    
    @action(methods=['POST'], detail=False, url_path='imprimir_consulta_aux')
    def imprimir_consulta_aux(self, request):
        try:
            return ConsultaService.imprimir_consulta_aux(request.data)
        except Exception:
            return Response("Error en el proceso por favor revisar.", status=status.HTTP_404_NOT_FOUND)
    
    @action(methods=['GET'], detail=False, url_path='centro_costos')
    def centro_costos(self, request, *args, **kwargs):
        return ConsultaService.centro_costos()
    
    @action(detail=False, methods=['POST'], url_path='exportar_consulta_filtro_aux')
    def exportar_consulta_filtro_aux(self, request, *args, **kwargs):
        return ConsultaService.exportar_consulta_filtro_aux(request.data)
    
    @action(detail=False, methods=['POST'], url_path='consulta_filtro_aux_banco')
    def consulta_filtro_aux_banco(self, request, *args, **kwargs):
        try:
            return Response(ConsultaService.filtro_aux_banco(request.data.get('model', {})))
        except Exception:
            return Response("Error en el proceso por favor revisar.", status=status.HTTP_404_NOT_FOUND)
    
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
        try:
            return ConsultaService.imprimir_consulta_aux_banco(request.data)
        except Exception:
            return Response("Error en el proceso por favor revisar.", status=status.HTTP_404_NOT_FOUND)
    
    @action(methods=['POST'], detail=False, url_path='consulta_balance_general')
    def consulta_balance_general(self, request):
        try:
            return Response(InformeService.filtro_balance_general(request.data['model']))
        except Exception:
            return Response("Error en el proceso por favor revisar.", status=status.HTTP_404_NOT_FOUND)
    
    @action(methods=['POST'], detail=False, url_path='imprimir_consulta_balance_general')
    def imprimir_consulta_balance_general(self, request):
        try:
            return InformeService.imprimir_consulta_balance_general(request.data['model'])
        except Exception:
            return Response("Error en el proceso por favor revisar.", status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['POST'], url_path='exportar_consulta_balance_general')
    def exportar_consulta_balance_general(self, request, *args, **kwargs):
        return InformeService.exportar_consulta_balance_general(request.data)

    @action(methods=['POST'], detail=False, url_path='consulta_balance_prueba')
    def consulta_balance_prueba(self, request):
        try:
            return Response(InformeService.filtro_balance_prueba(request.data['model']))
        except Exception:
            return Response("Error en el proceso por favor revisar.", status=status.HTTP_404_NOT_FOUND)
    
    @action(methods=['POST'], detail=False, url_path='imprimir_consulta_balance_prueba')
    def imprimir_consulta_balance_prueba(self, request):
        try:
            return InformeService.imprimir_consulta_balance_prueba(request.data)
        except Exception:
            return Response("Error en el proceso por favor revisar.", status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['POST'], url_path='exportar_consulta_balance_prueba')
    def exportar_consulta_balance_prueba(self, request, *args, **kwargs):
        return InformeService.exportar_consulta_balance_prueba(request.data)   
    
    @action(methods=['POST'], detail=False, url_path='consulta_estado_resultados')
    def consulta_estado_resultados(self, request):
        try:
            return Response(InformeService.filtro_estado_resultados(request.data['model']))
        except Exception:
            return Response("Error en el proceso por favor revisar.", status=status.HTTP_404_NOT_FOUND)
        
    @action(methods=['POST'], detail=False, url_path='imprimir_consulta_estado_resultados')
    def imprimir_consulta_estado_resultados(self, request):
        try:
            return InformeService.imprimir_consulta_estado_resultados(request.data['model'])
        except Exception:
            return Response("Error en el proceso por favor revisar.", status=status.HTTP_404_NOT_FOUND)
        
    @action(detail=False, methods=['POST'], url_path='exportar_consulta_estado_resultados')
    def exportar_consulta_estado_resultados(self, request, *args, **kwargs):
        numero = NumeroA()
        request.data['model']['mesfin'] = numero.mes_letra(request.data['model']['mesfin'])
        return InformeService.exportar_consulta_estado_resultados(request.data)  
    
    @action(methods=['POST'], detail=False, url_path='consulta_comprobrante_diario')
    def consulta_comprobrante_diario(self, request):
        query = []
        try:
            query.append(InformeService.filtro_comprobante_diario(request.data['model'], 1))
            query.append(InformeService.filtro_comprobante_diario(request.data['model'], 2))
            return Response(query)
        except Exception:
            return Response("Error en el proceso por favor revisar.", status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['POST'], url_path='exportar_consulta_comprobrante_diario')
    def exportar_consulta_comprobrante_diario(self, request, *args, **kwargs):
        return InformeService.exportar_consulta_comprobrante_diario(request.data)
    
    @action(methods=['POST'], detail=False, url_path='imprimir_consulta_comprobrante_diario')
    def imprimir_consulta_comprobrante_diario(self, request):
        try:
            request.data['model']['usuario'] = "{} {}".format(request.user.first_name, request.user.last_name).lower().capitalize()
            return InformeService.imprimir_consulta_comprobrante_diario(request.data)
        except Exception:
            return Response("Error en el proceso por favor revisar.", status=status.HTTP_404_NOT_FOUND)

        