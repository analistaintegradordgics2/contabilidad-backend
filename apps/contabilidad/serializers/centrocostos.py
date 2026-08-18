from rest_framework import serializers
from apps.contabilidad.models.parametros import CentroCostos

class CentroCostosSerializer(serializers.ModelSerializer):

    class Meta:
        model = CentroCostos
        fields = '__all__'

        