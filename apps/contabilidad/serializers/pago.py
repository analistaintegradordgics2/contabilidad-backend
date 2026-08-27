from rest_framework import serializers
from apps.contabilidad.models.pago import Banco, CuentaBancaria, FormaPago
from apps.utils.history import getHistorymodel

class BancosSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Banco
        fields = (
            "id",
            "codigo",
            "nombre",
            "estado"
        )


class CuentaBancariaSerializer(serializers.ModelSerializer):
    banco_nombre = serializers.CharField(source='banco.nombre', read_only=True)
    label = serializers.SerializerMethodField()

    class Meta:
        model = CuentaBancaria
        fields = (
            "id",
            "numero_cuenta",
            "nombre",
            "banco",
            "banco_nombre",
            "label",
            "activo"
        )

    def get_label(self, obj):
        if obj.nombre and obj.numero_cuenta:
            return f"{obj.numero_cuenta} - {obj.nombre}"
        return obj.numero_cuenta or obj.nombre or f"Cuenta #{obj.id}"

class FormaPagoSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = FormaPago
        fields = '__all__'
