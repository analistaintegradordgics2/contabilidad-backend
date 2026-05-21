from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.files.base import ContentFile
from backend.apps.personas.models.tributario import *
from backend.apps.personas.serializers.tributario import *

class RegimenTributarioViewSet(viewsets.ModelViewSet):
    # permission_classes = ()
    queryset = RegimenTributario.objects.all()
    serializer_class = RegimenTributarioModelSerializer

    def list(self, request, *args, **kwargs):
        query = self.get_queryset()
        data = RegimenTributarioModelSerializer(query, many=True).data
        return Response(data)

    @action(methods=['get'], detail=False, url_path='select')
    def select(self, request):
        filtro = {}
        if request.GET.get('serach', None) is not None:
            filtro['nombre__contains'] = request.GET.get('serach')
        queryset = RegimenTributario.objects.filter(**filtro)[:10]
        return Response(queryset.values('id', 'nombre'))

class ContribuyenteViewSet(viewsets.ModelViewSet):
    # permission_classes = ()
    queryset = Contribuyente.objects.all()
    serializer_class = ContribuyenteModelSerializer

    def list(self, request, *args, **kwargs):
        query = self.get_queryset()
        data = ContribuyenteModelSerializer(query, many=True).data
        return Response(data)

class TributarioViewSet(viewsets.ModelViewSet):
    # permission_classes = ()
    queryset = Tributario.objects.all().order_by('id')
    serializer_class = TributarioModelSerializer

    def list(self, request, *args, **kwargs):
        query = self.get_queryset()
        data = TributarioModelSerializer(query, many=True).data
        return Response(data)
