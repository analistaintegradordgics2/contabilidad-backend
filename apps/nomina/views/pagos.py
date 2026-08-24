from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from apps.nomina.services.pago_service import PagoService


class PagoEmpleadosViewSet(viewsets.ViewSet):

    def list(self, request, *args, **kwargs):
        periodo_id = request.GET.get("periodo")
        mes_id = request.GET.get("mes")
        anio_id = request.GET.get("anio")
        centro_costos_id = request.GET.get("centro_costos")

        try:
            resultado = PagoService.consultar_empleados_a_pagar(
                periodo_id=periodo_id,
                mes_id=mes_id,
                anio_id=anio_id,
                centro_costos_id=centro_costos_id
            )
            return Response({
                "status": 200,
                "data": resultado
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": 500,
                "data": None,
                "msg": f"Se presentó un error al consultar los empleados a pagar. Por favor, comuníquese con soporte técnico. {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        filtros = request.data.get("filtros", {})
        data = request.data.get("model", [])

        try:
            resultado = PagoService.pagar(filtros, data, user=request.user)
            return Response(resultado, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": 500,
                "data": None,
                "msg": f"Se presentó un error al generar la liquidación. Por favor, comuníquese con soporte técnico. {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['POST'], detail=False, url_path='generar_archivo')
    def generar_archivo(self, request, *args, **kwargs):
        filtros = request.data.get("filtros", {})
        data = request.data.get("model", [])
        try:
            return PagoService.generar_archivo(filtros, data)
        except Exception as e:
            return Response({
                "status": 500,
                "msg": f"Error al generar archivo: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['POST'], detail=False, url_path='exportar')
    def exportar(self, request, *args, **kwargs):
        try:
            return PagoService.exportar(request.data)
        except Exception as e:
            return Response({
                "status": 500,
                "msg": f"Error al exportar pagos: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['POST'], detail=False, url_path='imprimir')
    def imprimir(self, request, *args, **kwargs):
        try:
            return PagoService.imprimir(request.data)
        except Exception as e:
            return Response({
                "status": 500,
                "msg": f"Error al imprimir pagos: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)