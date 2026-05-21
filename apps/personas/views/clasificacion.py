from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from apps.utils.ModelViewSetClass import ModelViewSetClass
from apps.personas.serializers.clasificacion import *



class TipoDocumentoViewSet(viewsets.ModelViewSet):
    # permission_classes = ()
    queryset = TipoDocumento.objects.all().order_by('id')
    serializer_class = TipoDocumentoModelSerializer

    def list(self, request, *args, **kwargs):
        query = self.get_queryset()
        data = TipoDocumentoModelSerializer(query, many=True).data
        return Response(data)

    def retrieve(self, request, pk=None):
        queryset = TipoPersona.objects.all()
        qs = get_object_or_404(queryset, pk=pk)
        if len(qs.tipo_documento.all()) > 0:
            query = qs.tipo_documento.all()
        else:
            query = self.get_queryset()
        data = TipoDocumentoModelSerializer(query, many=True).data
        return Response(data)


class GenerosViewSet(viewsets.ModelViewSet):
    # permission_classes = ()
    queryset = Genero.objects.all()
    serializer_class = GeneroModelSerializer

    def list(self, request, *args, **kwargs):
        query = self.get_queryset()
        data = GeneroModelSerializer(query, many=True).data
        return Response(data)


class EstadoCivilViewSet(viewsets.ModelViewSet):
    # permission_classes = ()
    queryset = EstadoCivil.objects.all()
    serializer_class = EstadoCivilModelSerializer

    def list(self, request, *args, **kwargs):
        query = self.get_queryset()
        data = EstadoCivilModelSerializer(query, many=True).data
        return Response(data)

class TipoPersonaViewSet(ModelViewSetClass):
    # permission_classes = ()
    queryset = TipoPersona.objects.all().order_by('orden')
    serializer_class = TipoPersonaModelSerializer

    def list(self, request, *args, **kwargs):
        query = self.get_queryset().order_by('orden')
        data = TipoPersonaModelSerializer(query, many=True).data
        return Response(data)

    @action(methods=['get'], detail=False, url_path='select')
    def select(self, request):
        filtro = {}
        if request.GET.get('search', None) is not None:
            filtro['nombre__contains'] = request.GET.get('search')
        queryset = TipoPersona.objects.filter(**filtro)[:10]
        return Response(queryset.values('id', 'nombre'))


