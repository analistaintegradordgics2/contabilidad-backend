from apps.utils.ModelViewSetClass import ModelViewSetClass
from apps.contabilidad.serializers.cupon import *
from apps.contabilidad.services.cupon_service import CuponService
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from apps.contabilidad.models.cupon import Cupon
import pdb
from apps.parametros.serializers.parametrizacion import ParametrosModelSerializer

class CuponViewSet(ModelViewSetClass):
    queryset = Cupon.objects.filter(estado=True)

    def get_serializer_class(self):
        if not self.request.GET.get('sin_generar'):
            return CuponSinGenerarModelSerializer

        sin_generar = (
            self.request.GET.get('sin_generar', '').lower() == 'true'
        )

        if sin_generar:
            return CuponSinGenerarModelSerializer

        return CuponGeneradoModelSerializer
    
    def list(self, request, *args, **kwargs):
        sin_generar = request.GET.get('sin_generar', '').lower() == 'true'
        
        cupones = CuponService.listar(request.GET, sin_generar)
        
        serializer = self.get_serializer(cupones, many=True)
        return Response(serializer.data)
    
    @action(methods=['GET'], detail=False, url_path='parametros')
    def parametros_cupon(self, request, *args, **kwargs):
        parametros, tipos_documento = CuponService.parametros()
        data = {
            "parametros": ParametrosModelSerializer(parametros, many=True).data,
            "tipos_documento": tipos_documento
        }
        return Response(data, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False, url_path='parametros/save')
    def parametros_cupon_post(self, request, *args, **kwargs):
        data = request.data
        try:
           CuponService.GuardarParametros(data, request.user.id)
        except Exception as e:
            return Response({'msg': f"Error inesperado: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        return Response("ok", status=status.HTTP_200_OK)
    
    @action(methods=['POST'], detail=False, url_path='generar')
    def generar_cupon(self, request, *args, **kwargs):
        try:
            result = CuponService.generar(request.data, request.user.id)
        except Exception as e:
            return Response({'msg': f"Error inesperado: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(result, status=status.HTTP_200_OK)