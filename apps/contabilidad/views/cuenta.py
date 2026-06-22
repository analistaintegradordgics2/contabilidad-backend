import pdb

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q

from apps.utils.ModelViewSetClass import ModelViewSetClass
from apps.contabilidad.models.cuenta import Mayor
from apps.contabilidad.serializers.cuenta import MayorSerializer, MayorHistorySerializer
from apps.contabilidad.services.cuenta_service import *

class MayorViewSet(ModelViewSetClass):
    queryset = Mayor.objects.all().order_by('codigo')
    serializer_class = MayorSerializer

    def list(self, request, *args, **kwargs):
        query = self.get_queryset()
        data = MayorSerializer(query, many=True).data
        return Response(data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        mayor_id = request.data.get('id')

        # Validar si se puede inactivar
        if mayor_id and request.data.get('estado') == False:
            inactivar, mensaje = MayorService.inactivar_cuenta(
                mayor_id,
                request.data.get('codigo')
            )
            if not inactivar:
                return Response(
                    {'error': mensaje},
                    status=status.HTTP_400_BAD_REQUEST
                )

        mayor = MayorService.crear_o_actualizar(request.data, mayor_id)
        return Response(
            MayorSerializer(mayor).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(methods=['POST'], detail=False, url_path='validar_codigo')
    def validar_codigo(self, request):
        codigo    = request.data.get('codigo')
        mayor_id  = request.data.get('id', None)

        valido, mensaje = MayorService.validar_codigo(codigo, mayor_id)

        if not valido:
            return Response({'error': mensaje}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'valido': True}, status=status.HTTP_200_OK)
    
    @action(methods=['get'], detail=False, url_path='activos/(?P<tipo>[^/.]+)')
    def activos(self, request, tipo=None):
        queryset = Mayor.objects.filter(estado=True).order_by('codigo')
       
        tipo_filtro = 'General' if tipo == 'general' else 'Auxiliar'
        data = MayorSerializer(queryset.filter(tipo__icontains=tipo_filtro), many=True).data
        return Response(data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False, url_path='select')
    def select(self, request):
        search = request.GET.get('search', '')
        queryset =MayorService. get_mayor_select(search=search)
        return Response([MayorService.format_mayor_select(i) for i in queryset])

    @action(methods=['get'], detail=False, url_path='selectall')
    def selectall(self, request):
        search = request.GET.get('search', '')
        queryset = MayorService.get_mayor_select(solo_auxiliar=False, estado=None, search=search)
        return Response([MayorService.format_mayor_select(i) for i in queryset])

    @action(methods=['get'], detail=False, url_path='select-cuenta-banco')
    def select_cuenta_banco(self, request):
        search = request.GET.get('search', '')
        queryset = MayorService.get_mayor_select(rango=(1110, 11209999), search=search)
        return Response([MayorService.format_mayor_select(i) for i in queryset])

    @action(methods=['POST'], detail=False, url_path='selectnew')
    def selectnew(self, request, search=None):
        mayor_id = request.data.get('id')
        search   = request.data.get('search', '')
        todas    = request.data.get('todas', False)
        if mayor_id:
            item = Mayor.objects.filter(pk=mayor_id).first()
            return Response([MayorService.format_mayor_select(item, include_model=True)])

        queryset = MayorService.get_mayor_select(solo_auxiliar=not todas, search=search)
        return Response([MayorService.format_mayor_select(i, include_model=True) for i in queryset])

    @action(methods=['get'], detail=False, url_path='history/(?P<idmayor>[^/.]+)')
    def history(self, request, idmayor=None):
        query = Mayor.objects.filter(pk=idmayor).first()
        serializer = MayorHistorySerializer(query, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False, url_path='arbolpuc')
    def arbolpuc(self, request):
        return Response({
            'activas': MayorSerializer(Mayor.objects.filter(estado=True).order_by("codigo"), many=True).data,
            'inactivas': MayorSerializer(Mayor.objects.filter(estado=False).order_by("codigo"), many=True).data
        }, status=status.HTTP_200_OK)

    