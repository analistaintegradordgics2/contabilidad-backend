from apps.afiliados.serializers.afiliado import AfiliadoModelSerializer, AfiliadoResumenSerializer
from rest_framework import serializers
from apps.afiliados.models.cupon import Cupon, DetalleCupones
from apps.contabilidad.serializers.concepto import ConceptosSerializer
import pdb

class DetalleCuponModelSerializer(serializers.ModelSerializer):
    concepto = ConceptosSerializer()
    class Meta:
        model = DetalleCupones
        fields = ('id','detalle','valor','cantidad','piva','concepto')

class CuponSinGenerarModelSerializer(AfiliadoModelSerializer):
    pass

class CuponGeneradoModelSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Cupon
        fields = ('id','fecha','numero','nombre','direccion','telefono','ciudad','subtotal','iva','gran_total','fecha1','fecha2','pfecha2','valor1','valor2','detalle_cupones', 'descuento')

    detalle_cupones = DetalleCuponModelSerializer(many=True)

class CuponImprimirModelSerializer(CuponGeneradoModelSerializer):

    afiliado = serializers.SerializerMethodField('get_afiliado', read_only=True)
    def get_afiliado(self, obj):
        return AfiliadoResumenSerializer(obj.afiliado).data

    class Meta(CuponGeneradoModelSerializer.Meta):
        fields = CuponGeneradoModelSerializer.Meta.fields + (
            'afiliado',
        )