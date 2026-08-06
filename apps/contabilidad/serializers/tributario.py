from rest_framework import serializers
from apps.contabilidad.models.tributario import ReglaTributaria, VariableContable, ConceptoReglaTributaria


class VariableContableSerializer(serializers.ModelSerializer):
    class Meta:
        model = VariableContable
        fields = [
            'id',
            'codigo',
            'nombre',
            'descripcion',
            'es_sistema',
            'activa',
        ]


class ReglaTributariaSerializer(serializers.ModelSerializer):
    cuenta_contable_codigo = serializers.CharField(source='cuenta_contable.codigo', read_only=True)
    cuenta_contable_nombre = serializers.CharField(source='cuenta_contable.nombre', read_only=True)

    class Meta:
        model = ReglaTributaria
        fields = [
            'id',
            'nombre',
            'tipo_variable',
            'tarifa_porcentaje',
            'base_minima',
            'cuenta_contable',
            'cuenta_contable_codigo',
            'cuenta_contable_nombre',
            'vigencia_anio',
            'activa',
            'created',
            'modified',
        ]


class ConceptoReglaTributariaSerializer(serializers.ModelSerializer):
    concepto_nombre = serializers.CharField(source='concepto.nombre', read_only=True)
    regla_nombre = serializers.CharField(source='regla_tributaria.nombre', read_only=True)
    tipo_variable = serializers.CharField(source='regla_tributaria.tipo_variable', read_only=True)
    tarifa_porcentaje = serializers.DecimalField(source='regla_tributaria.tarifa_porcentaje', max_digits=7, decimal_places=4, read_only=True)

    class Meta:
        model = ConceptoReglaTributaria
        fields = [
            'id',
            'concepto',
            'concepto_nombre',
            'regla_tributaria',
            'regla_nombre',
            'tipo_variable',
            'tarifa_porcentaje',
            'activa',
        ]
