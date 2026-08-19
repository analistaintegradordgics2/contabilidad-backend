import pdb

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from apps.nomina.services.liquidacion_service import LiquidacionService

from apps.parametros.models.parametrizacion import Mes, Anio

class LiquidacionesViewSet(viewsets.ViewSet):

    def list(self, request, *args, **kwargs):
        anio = Anio.objects.get(pk=request.GET.get("anio"))
        mes = Mes.objects.get(pk=request.GET.get("mes")).numero
        periodo = request.GET.get("periodo", 3)
        centro_costo = request.GET.get("centro_costos", 0)

        validate, parametros_faltantes = LiquidacionService.validar_parametrizacion(anio)

        if validate == True :
            try:
                result = LiquidacionService.nominas_por_liquidar(anio, mes, periodo, centro_costo)
                return Response(result, status=status.HTTP_200_OK)
            except:
                return Response([], status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else :
            return Response({"msg": "Por favor primero parametrice el módulo de nómina antes de liquidar.", "parametros_faltantes": parametros_faltantes}, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        data = request.data
        try:
            resultado = LiquidacionService.liquidar(data, request.user)
            return Response({
                "status": 200,
                "data": resultado
            }, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({
                "status": 500,
                "data": None,
                "msg": f"Se presentó un error al generar la liquidación. Por favor, comuníquese con soporte técnico. {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
            

    @action(detail=False, methods=['GET'], url_path='vacaciones/(?P<contrato_novedad_id>[^/.]+)')
    def vacaciones(self, request, contrato_novedad_id=None, *args, **kwargs):
        return Response(LiquidacionService.vacaciones(contrato_novedad_id))

    @action(detail=False, methods=['POST'], url_path='liquidar_vacaciones')
    def liquidar_vacaciones(self, request, *args, **kwargs):
        data = request.data
        return LiquidacionService.liquidar_vacaciones(data, request.user)

    @action(detail=False, methods=['POST'], url_path='acciones')
    def acciones(self, request, *args, **kwargs):
        data = request.data
        whatsapp = data.get("whatsapp", False)
        email = data.get("email", False)

        if whatsapp == True or email == True :
            try:
                return Response(LiquidacionService.acciones(data))
            except Exception as e:
                return Response({
                    "status": 500,
                    "msg": f"Se presentó un error al generar la liquidación. Por favor, comuníquese con soporte técnico. {str(e)}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return LiquidacionService.acciones(data)

    @action(detail=False, methods=['POST'], url_path='anular')
    def anular(self, request):
        data = request.data
        try :
            result = LiquidacionService.anular(data, request.user)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": 400,
                "msg": f"Error al anular la liquidación. {str(e)}"
            }, status=status.HTTP_200_OK)
