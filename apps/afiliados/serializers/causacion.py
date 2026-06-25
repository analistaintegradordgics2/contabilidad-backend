from rest_framework import serializers
from apps.afiliados.models.causacion import ConceptoCausacion, AfiliadoConceptoCausacion
from apps.contabilidad.serializers.tipodocumento import TiposDocumentosListSerializer
from apps.contabilidad.serializers.concepto import ConceptosSerializer
from apps.contabilidad.serializers.cuenta import MayorSerializer

class ConceptoCausacionSerializer(serializers.ModelSerializer):

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
            
        return representation

class AfiliadoConceptoCausacionSerializer(serializers.ModelSerializer):

    class Meta:
        model = AfiliadoConceptoCausacion
        fields = '__all__'