from rest_framework import serializers
from apps.afiliados.models.causacion import FacturacionAfiliados, FacturacionDetalleAfiliados

import pdb


class FacturacionDetalleAfiliadosSerializer(serializers.ModelSerializer):

    class Meta:
        model = FacturacionDetalleAfiliados
        fields = (
            'id',
            'valor',
            'concepto_causacion_afiliado'
        )

    def to_representation(self, instance):
        from apps.afiliados.serializers.causacion import AfiliadoConceptoCausacionSerializer

        representation = super().to_representation(instance)

        conceptos_causacion = instance.concepto_causacion_afiliado
        if conceptos_causacion:
            representation['concepto_causacion_afiliado'] = AfiliadoConceptoCausacionSerializer(
                conceptos_causacion
            ).data

        return representation
    
class FacturacionAfiliadosSerializer(serializers.ModelSerializer):

    class Meta:
        model = FacturacionAfiliados
        exclude = ('afiliado','created', 'modified', 'delete', 'uc', 'um')

    def to_representation(self, instance):
        from apps.afiliados.serializers.afiliado import AfiliadoResumenSerializer

        representation = super().to_representation(instance)

        if instance.documento:
            representation['documento'] = {
                'id': instance.documento.id,
                'numero': instance.documento.numero,
                'fecha': instance.documento.fecha,
                'total': instance.documento.total,
                'detalle': instance.documento.detalle
            }

        representation["afiliado"] = AfiliadoResumenSerializer(
            instance.afiliado
        ).data

        representation["detalle"] = FacturacionDetalleAfiliadosSerializer(
            instance.afiliado_facturacion.all(),
            many=True
        ).data

        return representation