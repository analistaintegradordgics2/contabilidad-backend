from rest_framework import status
from rest_framework.decorators import action
from apps.utils.ModelViewSetClass import ModelViewSetClass
from rest_framework.response import Response

from apps.contabilidad.models.pago import Banco, CuentaBancaria
from apps.contabilidad.serializers.pago import BancosSerializer, CuentaBancariaSerializer

class PagoViewSet(ModelViewSetClass):
    queryset = Banco.objects.all().order_by('id')
    serializer_class = BancosSerializer

    def list(self, request, *args, **kwargs):
        query = self.get_queryset()
        data = BancosSerializer(query, many=True).data
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='cuentas')
    def cuentas(self, request):
        cuentas = CuentaBancaria.objects.filter(activo=True).order_by('id')
        data = CuentaBancariaSerializer(cuentas, many=True).data
        return Response(data, status=status.HTTP_200_OK)