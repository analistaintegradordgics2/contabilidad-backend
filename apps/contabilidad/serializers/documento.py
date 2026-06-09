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


class MovSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Mov
        fields = (
            'id', 'mayor', 'persona', 'concepto',
            'detalle', 'valor_db', 'valor_cr',
            'docref', 'base', 'centro_costos', 'nittercero',
        )


class DocumentoCreateSerializer(serializers.ModelSerializer):
    movimientos = MovSerializer(
        many=True,
        source='mov_documentos',  # related_name del FK
        required=False
    )

    class Meta:
        model  = Documentos
        fields = (
            'id', 'numero', 'fecha',
            'tipo_documento', 'concepto', 'detalle',
            'personas', 'estado',
            'gtotal',
            'movimientos',
        )


    def update(self, instance, validated_data):
        movimientos_data = validated_data.pop('mov_documentos', [])
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()
        # Reemplazar movimientos
        instance.mov_documentos.all().delete()
        self._guardar_movimientos(instance, movimientos_data)
        return instance

