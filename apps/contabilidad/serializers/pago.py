from rest_framework import serializers
from apps.contabilidad.models.pago import Banco
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


        