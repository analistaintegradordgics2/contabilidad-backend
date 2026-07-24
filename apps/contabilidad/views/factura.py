from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from apps.contabilidad.models.parametros import EstadoFactElectro
from apps.contabilidad.serializers.factura import EstadosFactSerializer
from apps.contabilidad.services.factura_service import FacturaService
from apps.contabilidad.services.factura_transmision_service import FacturacionTransmisionService, FacturacionElectronicaError


class EstadosFactViewSet(viewsets.ModelViewSet):
    queryset = EstadoFactElectro.objects.all()
    serializer_class = EstadosFactSerializer

    def list(self, request, *args, **kwargs):
        query = self.get_queryset()
        data = EstadosFactSerializer(query, many=True).data
        return Response(data, status=status.HTTP_200_OK)


class TransmisionFacturaViewSet(viewsets.ModelViewSet):

    @action(methods=['post'], detail=False, url_path='consulta_fact_electronica')
    def consulta_fact_electronica(self, request):
        try:
            data = FacturaService.consulta_fact_electronica(request.data)
            return Response(data)
        except Exception as e:
            return Response(str(e), status=400)
    
    @action(methods=['post'], detail=False, url_path='transmitir')
    def transmitir(self, request):
        facturas = request.data['facturas']

        try:
            service = FacturacionTransmisionService(usuario=request.user.username)
            resultado = service.transmitir_facturas(facturas)
            return Response(resultado, status=status.HTTP_200_OK)
        except FacturacionElectronicaError as e:
            return Response({"status": e.status_code, "msg": e.message}, status=status.HTTP_200_OK)