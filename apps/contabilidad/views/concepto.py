from rest_framework import status
from apps.utils.ModelViewSetClass import ModelViewSetClass
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import CharField, Value
from django.db.models.functions import Concat, Cast

from apps.contabilidad.models.concepto import Concepto
from apps.contabilidad.serializers.concepto import ConceptosSerializer, ConceptoHistorySerializer

class ConceptosViewSet(ModelViewSetClass):
    queryset = Concepto.objects.all().order_by('codigo')
    serializer_class = ConceptosSerializer

    def list(self, request, *args, **kwargs):
        query = self.get_queryset()
        data = ConceptosSerializer(query, many=True).data
        return Response(data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        request.data['codigo'] = int(request.data['codigo'])
        serializer = ConceptosSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        request.data['codigo'] = int(request.data['codigo'])
        serializer = ConceptosSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False, url_path='validar_codigo')
    def validar_codigo(self, request):
        codigo = request.data.get('codigo')
        concepto_id = request.data.get('id')

        if not codigo:
            return Response(
                {'error': 'El código es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Buscar si ya existe
        existe = Concepto.objects.filter(codigo=codigo)

        # Si es edición, excluir el mismo registro
        if concepto_id:
            existe = existe.exclude(id=concepto_id)

        if existe.exists():
            return Response(
                {'error': 'El código ya existe'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({'ok': True}, status=status.HTTP_200_OK)
    
    @action(methods=['get'], detail=False, url_path='history/(?P<idconcepto>[^/.]+)')
    def history(self, request, idconcepto=None):
        query = Concepto.objects.filter(pk=idconcepto).first()
        serializer = ConceptoHistorySerializer(query, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    
    @action(methods=['POST'], detail=False, url_path='selectnew/(?P<search>[^/.]+)')
    def selectnew(self, request, search=None):
        concepto_id = request.data.get('id')
        search = request.data.get('search', '')

        if concepto_id:
            queryset = Concepto.objects.filter(pk=concepto_id)
        else:
            queryset = Concepto.objects.annotate(
                codigo_nombre=Concat(
                    Cast('codigo', CharField()),
                    Value(' - '),
                    'nombre',
                    output_field=CharField()
                )
            ).filter(codigo_nombre__icontains=search).order_by('codigo')[:10]

        result = [
            {
                'value': item.id,
                'label': f"{item.codigo} - {item.nombre}",
                'detalle': item.detalle
            }
            for item in queryset
        ]
        return Response(result, status=status.HTTP_200_OK)
    
   