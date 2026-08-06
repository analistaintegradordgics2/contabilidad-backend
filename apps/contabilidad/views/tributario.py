from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import AllowAny
from apps.utils.ModelViewSetClass import ModelViewSetClass
from apps.contabilidad.models.tributario import ReglaTributaria, VariableContable, ConceptoReglaTributaria
from apps.contabilidad.serializers.tributario import ReglaTributariaSerializer, VariableContableSerializer, ConceptoReglaTributariaSerializer


class VariableContableViewSet(ModelViewSetClass):
    queryset = VariableContable.objects.filter(activa=True).order_by('nombre')
    serializer_class = VariableContableSerializer

    @action(detail=False, methods=['GET'], url_path='todas')
    @permission_classes([AllowAny])
    def todas(self, request):
        vars_qs = VariableContable.objects.filter(activa=True).order_by('nombre')
        return Response(VariableContableSerializer(vars_qs, many=True).data)


class ReglaTributariaViewSet(ModelViewSetClass):
    queryset = ReglaTributaria.objects.filter(activa=True).order_by('tipo_variable', 'nombre')
    serializer_class = ReglaTributariaSerializer

    @action(detail=False, methods=['GET'], url_path='todas')
    @permission_classes([AllowAny])
    def todas(self, request):
        reglas = ReglaTributaria.objects.all().order_by('tipo_variable', 'nombre')
        return Response(ReglaTributariaSerializer(reglas, many=True).data)


class ConceptoReglaTributariaViewSet(ModelViewSetClass):
    queryset = ConceptoReglaTributaria.objects.filter(activa=True)
    serializer_class = ConceptoReglaTributariaSerializer

    @action(detail=False, methods=['GET'], url_path='por-concepto/(?P<concepto_id>[^/.]+)')
    def por_concepto(self, request, concepto_id=None):
        reglas = ConceptoReglaTributaria.objects.filter(concepto_id=concepto_id, activa=True)
        return Response(ConceptoReglaTributariaSerializer(reglas, many=True).data)
