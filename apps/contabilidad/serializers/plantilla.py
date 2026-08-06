from rest_framework import serializers
from apps.contabilidad.models.plantilla import PlantillaDocumento, PlantillaMovimiento
from apps.contabilidad.models.cuenta import Mayor
from apps.contabilidad.models.concepto import Concepto
from apps.contabilidad.models.tipodocumento import TiposDocumentos


class PlantillaMovimientoSerializer(serializers.ModelSerializer):
    mayor_codigo = serializers.CharField(source='mayor.codigo', read_only=True)
    mayor_nombre = serializers.CharField(source='mayor.nombre', read_only=True)
    concepto_nombre = serializers.CharField(source='concepto.nombre', read_only=True)
    regla_tributaria_nombre = serializers.CharField(source='regla_tributaria.nombre', read_only=True)

    class Meta:
        model = PlantillaMovimiento
        fields = [
            'id',
            'plantilla',
            'mayor',
            'mayor_codigo',
            'mayor_nombre',
            'concepto',
            'concepto_nombre',
            'naturaleza',
            'tipo_valor',
            'origen_valor',
            'regla_tributaria',
            'regla_tributaria_nombre',
            'valor_fijo',
            'porcentaje',
            'base_minima',
            'usa_tercero',
            'detalle_default',
            'orden',
        ]


class PlantillaDocumentoSerializer(serializers.ModelSerializer):
    movimientos = PlantillaMovimientoSerializer(many=True, read_only=True)
    fuente_nombre = serializers.CharField(source='fuente.nombre', read_only=True)
    tipo_documento_nombre = serializers.CharField(source='tipo_documento.nombre', read_only=True)
    concepto_nombre = serializers.CharField(source='concepto.nombre', read_only=True)

    class Meta:
        model = PlantillaDocumento
        fields = [
            'id',
            'nombre',
            'descripcion',
            'fuente',
            'fuente_nombre',
            'tipo_documento',
            'tipo_documento_nombre',
            'concepto',
            'concepto_nombre',
            'activa',
            'icono',
            'color',
            'requiere_tercero',
            'requiere_valor',
            'contador_usos',
            'ultima_fecha_uso',
            'movimientos',
            'created',
            'modified',
        ]
