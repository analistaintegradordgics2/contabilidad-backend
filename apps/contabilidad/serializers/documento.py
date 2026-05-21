from rest_framework import serializers
from apps.contabilidad.models.documento import Documentos, Mov, PagoDocumento, FactElectronicaDocumento, DocumentosBita

class MovSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mov
        fields = '__all__'


class PagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PagoDocumento
        fields = '__all__'


class FactElectronicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = FactElectronicaDocumento
        fields = '__all__'


class DocumentoSerializer(serializers.ModelSerializer):

    movimientos = MovSerializer(many=True, write_only=True)
    pagos = PagoSerializer(many=True, required=False)
    facturacion = FactElectronicaSerializer(required=False)

    class Meta:
        model = Documentos
        fields = '__all__'

    def create(self, validated_data):
        raise NotImplementedError("Usar DocumentoService")

class DocumentosBitaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentosBita
        fields = '__all__'