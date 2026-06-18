from rest_framework import status
from apps.utils.ModelViewSetClass import ModelViewSetClass
from rest_framework.response import Response

from apps.contabilidad.models.pago import Banco
from apps.contabilidad.serializers.pago import BancosSerializer

class PagoViewSet(ModelViewSetClass):
    queryset = Banco.objects.all().order_by('id')
    serializer_class = BancosSerializer

    def list(self, request, *args, **kwargs):
        query = self.get_queryset()
        data = BancosSerializer(query, many=True).data
        return Response(data, status=status.HTTP_200_OK)


    
   