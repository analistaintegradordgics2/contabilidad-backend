from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from django.db.models import F
from django.db.models import Q
from django.db.models.functions import Concat
from django.db.models import Value
from apps.utils.ModelViewSetClass import ModelViewSetClass
from apps.utils.list import lists

from apps.personas.serializers.contacto import *


class TipoContactoViewSet(viewsets.ModelViewSet):
    # permission_classes = ()
    queryset = TipoContacto.objects.all()
    serializer_class = TipoContactoModelSerializer

    def list(self, request, *args, **kwargs):
        query = self.get_queryset()
        data = TipoContactoModelSerializer(query, many=True).data
        return Response(data)

    @action(detail=False, methods=['get'], url_path='tipodireccion')
    def tipodireccion(self,request):

        tipo_direccion = TipoContacto.objects.filter().exclude(nombre='Personal')
        serializer = TipoContactoModelSerializer(tipo_direccion, many=True).data
        return Response(serializer, status=status.HTTP_200_OK)

class TelefonoViewSet(ModelViewSetClass):
    # permission_classes = ()
    queryset = Telefono.objects.all()
    serializer_class = TelefonoModelSerializer

    def list(self, request, *args, **kwargs):
        query = self.get_queryset()
        data = TelefonoModelSerializer(query, many=True).data
        return Response(data)

    @action(methods=['get'], detail=False, url_path='select')
    def select(self, request):
        filtro = {}
        queryset = Telefono.objects.all()[:10]

        if request.GET.get('search', None) is not None:
            try:
                valor = int(request.GET.get('search'))
                queryset = Telefono.objects.filter(valor__icontains=valor)[:10]
            except:
                filtro = request.GET.get('search').upper()
                queryset = Telefono.objects.annotate(pn_pa_search=Concat('persona__p_nombre', Value(' '), 'persona__p_apellido')).filter(Q(persona__n_completo__icontains=filtro) | Q(pn_pa_search__icontains=filtro))[:10]

        return Response(queryset.values('persona_id', nombre=Concat( F('valor'), Value(' - ') , F('persona__n_completo'))))
    
    @action(detail=False, methods=['get'], url_path='prefijo_telefonos')
    def prefijo_telefonos(self,request):

        return Response(lists.prefijos_telefono)
