import pdb, json
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from apps.parametros.models.parametrizacion import Parametros
from apps.nomina.services.transmision_service import TransmisionService
from apps.nomina.services.transmitir_nomina_service import TransmitirNominaService, NominaElectronicaParametrizacionError
from apps.nomina.models.contratos import ContratoNomina
from apps.nomina.serializers.contratos import ContratosFuncionalidadSerializer
from apps.nomina.models.transmision import NominaElectronica
from apps.nomina.serializers.transmision import NominaElectronicaSerializer, NominaElectronicaListSerializer
from apps.parametros.models.parametrizacion import Mes, Anio

class TransmisionViewSet(viewsets.ModelViewSet):
    queryset = NominaElectronica.objects.all()
    serializer_class = NominaElectronicaSerializer

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
            # Funcionalidad
            mes = Mes.objects.get(pk=mes)
            anio = Anio.objects.filter(nombre=anio).first()
            nomina_elect = NominaElectronica.objects.filter(mes_id=mes.id, anio_id=anio.id)
            nomina_elect = NominaElectronicaListSerializer(nomina_elect, many=True).data
            return Response(nomina_elect, status=status.HTTP_200_OK)

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

    @action(methods=['POST'], detail=False, url_path='archivos_transmision')
    def archivos_transmision(self, request):
        return TransmisionService.archivos_transmision()

    @action(methods=['GET'], detail=False, url_path='contratos')
    def ContratosFuncionalidad(self, request):

        contratos = ContratoNomina.objects.all()
        contratos = ContratosFuncionalidadSerializer(contratos, many=True).data

        return Response(contratos, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False, url_path='preguardar_funcionalidad')
    def PreguardarFuncionalidad(self, request):
        data = request.data
        try :
            if data["id"] == None :
                # Nuevo
                data["uc"] = request.user.id
                nomina_elect = self.get_serializer(data=data)
            else :
                # Editar
                data["um"] = request.user.id
                nomina_elect = self.get_serializer(self.get_queryset().get(pk=data["id"]), data=data)
            nomina_elect.is_valid(raise_exception=True)
            nomina_elect.save()
            return Response({
                "status": 200,
                "msg": "Nómina conciliada correctamente."
            }, status=status.HTTP_200_OK)
        except Exception as inst:
            return Response({
                "status": 400,
                "msg": "Se presentó un error en el proceso, por favor comuníquese con soporte.",
                "error": str(inst)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
