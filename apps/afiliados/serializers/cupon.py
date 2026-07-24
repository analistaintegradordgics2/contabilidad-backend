from apps.afiliados.serializers.afiliado import AfiliadoModelSerializer, AfiliadoResumenSerializer
from rest_framework import serializers
from apps.afiliados.models.cupon import Cupon, DetalleCupones
from apps.contabilidad.serializers.concepto import ConceptosSerializer
import pdb

class DetalleCuponModelSerializer(serializers.ModelSerializer):
    concepto = ConceptosSerializer()
    valor = serializers.SerializerMethodField()

    class Meta:
        model = DetalleCupones
        fields = ('id','detalle','valor','cantidad','piva','concepto')

    def get_valor(self, obj):
        if obj.valor is None:
            return 0
        val = float(obj.valor)
        if (obj.concepto_causacion and obj.concepto_causacion.es_retencion) or val < 0:
            return -abs(val)
        return val

class CuponSinGenerarModelSerializer(AfiliadoModelSerializer):
    pass

class CuponGeneradoModelSerializer(serializers.ModelSerializer):
    retefuente = serializers.SerializerMethodField()
    reteiva = serializers.SerializerMethodField()
    reteica = serializers.SerializerMethodField()
    
    class Meta:
        model = Cupon
        fields = ('id','fecha','numero','nombre','direccion','telefono','ciudad','subtotal','iva','gran_total','fecha1','fecha2','pfecha2','valor1','valor2','detalle_cupones', 'descuento', 'retefuente', 'reteiva', 'reteica')

    detalle_cupones = DetalleCuponModelSerializer(many=True)

    def get_retefuente(self, obj):
        val = obj.retefuente or 0
        return -abs(float(val)) if val else 0

    def get_reteiva(self, obj):
        val = obj.reteiva or 0
        return -abs(float(val)) if val else 0

    def get_reteica(self, obj):
        val = obj.reteica or 0
        return -abs(float(val)) if val else 0

class CuponImprimirModelSerializer(CuponGeneradoModelSerializer):

    afiliado = serializers.SerializerMethodField('get_afiliado', read_only=True)
    def get_afiliado(self, obj):
        return AfiliadoResumenSerializer(obj.afiliado).data

    class Meta(CuponGeneradoModelSerializer.Meta):
        fields = CuponGeneradoModelSerializer.Meta.fields + (
            'afiliado',
        )