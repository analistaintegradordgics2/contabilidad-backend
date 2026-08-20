import pdb, json
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from apps.parametros.models.parametrizacion import Parametros
from apps.nomina.services.transmision_service import TransmisionService
from apps.nomina.services.transmitir_nomina_service import TransmitirNominaService, NominaElectronicaParametrizacionError

class TransmisionViewSet(viewsets.ModelViewSet):
    def list(self, request, *args, **kwargs):
        anio = request.GET.get("anio")
        mes = request.GET.get("mes")

        funcionalidad_nomina = Parametros.objects.filter(parametro='funcionalidad_nomina', valor__iexact='true').exists()

        if not funcionalidad_nomina:
            try:
                result = TransmisionService.list(anio, mes)
                return Response(result, status=status.HTTP_200_OK)
            except:
                return Response([], status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            pass

    def create(self, request, *args, **kwargs):
        filtros = request.data["filtros"]
        data = request.data["data"]
 
        try:
            service = TransmitirNominaService(user=request.user)
        except NominaElectronicaParametrizacionError as exc:
            return Response({"status": 400, "msg": exc.msg}, status=status.HTTP_200_OK)
 
        resultado = service.transmitir(filtros, data)
 
        if resultado.get("server_error"):
            return Response(resultado, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
        return Response(resultado, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False, url_path='archivos_transmision')
    def archivos_transmision(self, request):
        return TransmisionService.archivos_transmision()
