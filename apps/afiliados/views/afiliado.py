from apps.afiliados.serializers.afiliado import *
from apps.personas.models.persona import Persona
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from apps.afiliados.services.afiliado_service import AfiliadoService
from apps.afiliados.models.afiliado import Afiliado
from rest_framework.decorators import action
import pdb

class AfiliadoViewSet(viewsets.ModelViewSet):
    queryset = Afiliado.objects.filter(activo=True)
    serializer_class = AfiliadoModelSerializer
    pagination_class = None

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            service = AfiliadoService(request.user)
            try:
                afiliado = service.create_afiliado(serializer.validated_data)
            except Exception as e:
                return Response({'msg': f"Error inesperado: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
            return Response(self.get_serializer(afiliado).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        # pdb.set_trace()
        request.data['aplicativo'] = request.data['aplicativo']['id']
        request.data['persona'] = request.data['persona']['id']
        request.data['tipo_contrato'] = request.data['tipo_contrato']['id']
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        service = AfiliadoService(request.user)
        try:
            afiliado = service.update_afiliado(kwargs['pk'], data=serializer.validated_data)
        except Afiliado.DoesNotExist:
            return Response({'msg': 'Afiliado no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        return Response(self.get_serializer(afiliado).data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='personas')
    def personas(self, request, *args, **kwargs):
        queryset = Persona.objects.filter(personas_tipos_personas_persona__tipo_persona__nombre__iexact='Afiliado')
        serializer = AfiliadoListSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)