from rest_framework import serializers
from apps.afiliados.models.causacion import ConceptoCausacion, AfiliadoConceptoCausacion
from apps.contabilidad.serializers.tipodocumento import TiposDocumentosListSerializer
from apps.contabilidad.serializers.concepto import ConceptosSerializer
from apps.contabilidad.serializers.cuenta import MayorSerializer

from apps.contabilidad.models.parametros import TipoRetencion

class ConceptoCausacionSerializer(serializers.ModelSerializer):
    retenciones = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=TipoRetencion.objects.all(),
        required=False
    )

    class Meta:
        model = ConceptoCausacion
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        if instance.tipo_factura:
            representation['tipo_factura'] = TiposDocumentosListSerializer(instance.tipo_factura).data
            
        if instance.concepto:
            representation['concepto'] = ConceptosSerializer(instance.concepto).data
            
        if instance.mayor:
            representation['mayor'] = MayorSerializer(instance.mayor).data

        if instance.tipo_retencion:
            representation['tipo_retencion'] = {
                'id': instance.tipo_retencion.id,
                'nombre': instance.tipo_retencion.nombre,
                'porcentaje_defecto': instance.tipo_retencion.porcentaje_defecto,
                'base_sobre': instance.tipo_retencion.base_sobre,
            }

        representation['retenciones'] = [
            {
                'id': r.id,
                'nombre': r.nombre,
                'porcentaje_defecto': r.porcentaje_defecto,
                'base_sobre': r.base_sobre,
            }
            for r in instance.retenciones.all()
        ]
            
        return representation

class AfiliadoConceptoCausacionSerializer(serializers.ModelSerializer):

    nombreConcepto = serializers.SerializerMethodField('get_n_concepto', read_only=True)
    valor = serializers.SerializerMethodField()

    def get_n_concepto(self, obj):
        try:
            return obj.concepto.nombre
        except:
            return {}

    def get_valor(self, obj):
        if obj.valor is None:
            return 0
        val = float(obj.valor)
        if obj.concepto and obj.concepto.es_retencion:
            return -abs(val)
        return val

    class Meta:
        model = AfiliadoConceptoCausacion
        fields = ('id','nombreConcepto','valor','detalle','porcentaje','facturar','concepto')